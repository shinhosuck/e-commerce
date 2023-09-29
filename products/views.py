from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.utils import timezone
from .context_processors import get_basket_total
from .models import (
    Product, 
    ProductImage,  
    ProductCategory,
    ProductSubCategory,
    ProductReview,
    Order,
    Checkout,
    ShippingAddress,
    CheckoutReceipt,
)
from .forms import (
    CreateProductForm, 
    CreateProductImageForm, 
    ProductReviewForm,
    ShippingAddressForm,
)

from django.conf import settings
import stripe
import json
from decimal import Decimal



stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

def home_view(request):
    category = ProductCategory.objects.all()
    products = Product.objects.all()
    for product in products:
        product.save()
    context = {'category': category}
    return render(request, 'products/home.html', context)


def product_list_view(request):
    query_set = Product.objects.all()
    laptops = query_set.filter(category__name__iexact='laptop')
    entry_level = laptops.filter(sub_category__name__iexact='entry-level')
    context = {'query_set': query_set[0:6], 'laptops':laptops[0:6], 'entry_level':entry_level[0:6]}
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, id):
    user = request.user
    context = {}
    try:
        query = Product.objects.get(id=id)
        reviews = query.productreview_set.all()
        images = query.productimage_set.all()
    except Exception as e:
        messages.error(request, f'{e}')
        return redirect('products:home')
    
    context['query'] = query
    context['images'] = images
    context['reviews'] = reviews

    # checks if customer has purchased this product
    if user.is_authenticated:
        checkouts = user.checkout_set.filter(open=False)

        # this is to check if customer previously has written a review on this product
        has_review = user.productreview_set.filter(product__id=id).first()

        if checkouts.exists():
            for checkout in checkouts:
                orders = checkout.order.filter(product__id=id)
                if orders.exists():
                    context['purchase_verified'] = True
                if has_review: # if this is true, customer will be updating the review
                    context['has_review'] = True
                    context['review_id'] = has_review.id
    return render(request, 'products/product_detail.html', context)


@login_required()
def product_create_view(request):
    query_set = ProductSubCategory.objects.all()

    category_name = []
    sub_categories = []

    for obj in query_set:
        if obj.category.name not in category_name:
            category_name.append(obj.category.name)
            sub_categories.append({'id':obj.category.id ,'category_name':obj.category.name, 'sub_categories':[{'id':obj.id, 'name':obj.name}]})
        else:
            for sub_cat in sub_categories:
                for key, value in sub_cat.items():
                    if value == obj.category.name:
                        sub_cat['sub_categories'] += [{'id':obj.id, 'name':obj.name}]
    
    image_form = CreateProductImageForm(request.POST or None, request.FILES or None)
    product_form = CreateProductForm(request.POST or None, request.FILES or None)
    context = {
        'product_form': product_form,
        'image_form': image_form,
        'sub_categories': json.dumps(sub_categories)
    }
    if image_form.is_valid() and product_form.is_valid():
        images = request.FILES.getlist('image')
        product = product_form.save()
        for img in images:
            ProductImage.objects.create(product=product, image=img)
    return render(request, 'products/product_create.html', context)


@login_required
def write_product_review_view(request, id):
    existing_review = ProductReview.objects.filter(id=request.GET.get('update')).first()
    product = Product.objects.get(id=id)
    user = request.user

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            author = request.user
            content = form.cleaned_data.get('content')
            rating = int(form.cleaned_data.get('rating'))
            title = form.cleaned_data.get('title')

            if existing_review:
                existing_review.rating=rating
                existing_review.title = title
                existing_review.content=content
                existing_review.save()
                product.likes = existing_review.calculate_rating()
                product.save()
                messages.success(request, f'{author.username}, thank you for the review!')
                return redirect('products:product-detail', id)
            
            else:
                new_review = ProductReview.objects.create(
                    product=product, 
                    author=author, 
                    rating=rating, 
                    title = title,
                    content=content
                )
                product.likes = new_review.calculate_rating()
                product.save()
            messages.success(request, f'{author.username}, thank you for the review!')
            return redirect('products:product-detail', id)
        
        messages.error(request, 'There was an error. Try again later.')
        return redirect('products:product-review', id)
    else:
        checkouts = Checkout.objects.filter(customer=user, open=False)
        if not checkouts.exists():
            messages.error(request, 'You are not authorized to write review on this product.')
            return redirect('products:product-detail', id)
        elif checkouts.exists():
            purchase_verified = []
            for checkout in checkouts:
                orders = checkout.order.all().filter(product=product)
                for order in orders:
                    if order.product == product:
                        purchase_verified.append(order)
            if purchase_verified:
                context= {'query': product}
                if existing_review:
                    context['existing_review_id'] = existing_review.id
                    context['existing_review'] = existing_review
                return render(request, 'products/product_review.html', context)
            else:
                messages.error(request, 'You are not authorized to write review on this product.')
                return redirect('products:product-detail', id)
    
    
def product_search_view(request):
    q = request.GET.get('q')
    query_set = Product.objects.filter(Q(category__name__icontains = q) | 
            Q(sub_category__name__icontains = q) | Q(name__icontains = q))
    context = {'query_set': query_set, 'q':q}
    return render(request, 'products/search_result.html', context)


@login_required
def add_to_basket_view(request, id):
    product = Product.objects.get(id=id)
    order = Order.objects.filter(customer=request.user ,product=product, open=True).first()
    if order:
        order.quantity += 1
        order.save()
        messages.success(request, f'{product.name} quantity has been updated.')
        return redirect('products:product-basket')
    else:
        Order.objects.create(customer=request.user, product=product, quantity=1)
        messages.success(request, f'{product.name} has been added to the basket.')
        return redirect('products:product-basket')


@login_required
def basket_view(request):
    user = request.user
    query_set = user.order_set.all().filter(open=True)
    context = {'query_set': query_set}

    if not query_set.exists():
        messages.info(request, 'Your basket is empty.')
        return redirect('products:product-list')
    
    return render(request, 'products/basket.html', context)


@login_required
def update_basket_view(request, id):
    user = request.user
    qty = request.GET.get('amount')
    order = Order.objects.get(customer=user, product__id=id, open=True)

    if int(qty) == 0 or order.quantity == int(qty):
        order.delete()
        messages.success(request, f'{order.product.name} has been deleted from your basket.')
        return redirect('products:product-basket')
    
    order.quantity = int(qty)
    order.save()
    messages.success(request, f'{order.product.name} quantity has been updated.')
    return redirect('products:product-basket')


@login_required
def customer_address_view(request):
    instance = ShippingAddress.objects.filter(customer=request.user).first()
    form = ShippingAddressForm(instance=instance)
    context = {'form': form}

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=instance)
        if form.is_valid():
            shipping_address = form.save()
            shipping_address.customer = request.user
            shipping_address.save()
            return redirect('products:checkout-summary')
        else:
            context['form'] = form
    return render(request, 'products/address.html', context)


@login_required 
def checkout_summary_view(request):
    query_set = Order.objects.filter(customer=request.user, open=True)

    if not query_set.exists():
        messages.error(request, 'You do not have any pending orders.')
        return redirect('products:product-list')
    
    context = {'query_set': query_set}
    return render(request, 'products/checkout_summary.html', context)


@login_required
def checkout_view(request):
    user= request.user
    orders = Order.objects.filter(customer__username=user, open=True)

    try:
        checkout = Checkout.objects.get(customer=user, open=True)
    except:
        checkout = Checkout.objects.create(customer=user)
        for product in orders:
            checkout.order.add(product)
        checkout.set_amount_due()
        checkout.save()
        return redirect('products:checkout-session', checkout.id)

    for product in orders:
        checkout.order.add(product)
    checkout.set_amount_due()
    checkout.save()
    return redirect('products:checkout-session', checkout.id)


@login_required 
def create_checkout_session_view(request, id):
    DOMAIN = 'http://127.0.0.1:8000/'

    try:
        checkout_obj = Checkout.objects.get(id=id, open=True)
    except:
        messages.error(request, 'You do not have any pending orders.')
        return redirect('products:product-list')
    
    total = get_basket_total(request)['total'].replace(',','')
    total = int(Decimal(total)*100)

    amount_due = int((checkout_obj.total_amount_due) * 100)
    checkout_session = stripe.checkout.Session.create(
        line_items=[{ 
                'price_data': { 
                    'currency': 'php', 
                    'unit_amount': f'{total}',
                    'product_data':{ 
                        'name': 'Total amount due'
                        }, 
                },
                'quantity': 1
            }],
        metadata={'receipt_url': 'http://127.0.0.1:8000/payment/success/7/'},
        mode='payment',
        success_url=DOMAIN + f'payment/success/{id}/',
        cancel_url=DOMAIN + 'payment/cancel/',
    )
    return redirect(checkout_session.url, code=303)


@login_required
def payment_cancel_view(request):
    return render(request, 'products/payment_cancel.html')


@login_required
def payment_success_view(request, id):
    DOMAIN = 'http://127.0.0.1:8000'
    customer = request.user
    orders = customer.order_set.filter(open=True)
    checkout_obj = Checkout.objects.filter(id=id, open=True).first()

    context = {
        'domain': DOMAIN,
        'basket_total': get_basket_total(request),
    }

    if not orders.exists() and not checkout_obj:
        messages.error(request, 'You do not have any pending orders.')
        return redirect('products:order-history')
    
    your_purchase = ''

    for item in checkout_obj.order.all():
        discount = ''
        if item.product.get_discount_price():
            discount = item.product.price - Decimal(item.product.get_discount_price().replace(',',''))
            discount = f'{str(discount)[0:-6]},{str(discount)[-6:]}'
        else:
            discount = 0
        your_purchase += f'''
        Customer: {checkout_obj.customer.username},
        Product name: {item.product.name}, 
        Price: P{item.product.price_str_format}, 
        Discount price: P{item.product.discount_price_str_format},
        Saved: P{discount}, 
        Quantity: {item.quantity},
        item_url: {DOMAIN}{item.product.get_absolute_url()}
        --------------------------------------------------
        '''
    if get_basket_total(request)['discount_amount']:
        your_purchase += 'Savings: {0}\n'.format(get_basket_total(request)['discount_amount'])
    your_purchase += 'Sub-total: {0},{1}\n'.format(str(checkout_obj.set_amount_due())[0:-6], str(checkout_obj.set_amount_due())[-6:])
    your_purchase += 'VAT: {0}\n'.format(get_basket_total(request)['vat'])
    your_purchase += 'Total: {0}'.format(get_basket_total(request)['total'])

    # create CheckoutReceipt
    receipt = CheckoutReceipt.objects.create(
        checkout=checkout_obj, 
        customer=customer, 
        checkout_summary=your_purchase,
        saving = '{0}'.format(get_basket_total(request)['discount_amount']),
        sub_total = '{0},{1}'.format(str(checkout_obj.set_amount_due())[0:-6], str(checkout_obj.set_amount_due())[-6:]),
        tax = '{0}'.format(get_basket_total(request)['vat']),
        total = '{0}'.format(get_basket_total(request)['total'])
    )

    address = ShippingAddress.objects.get(customer=request.user)
    email_from = settings.EMAIL_HOST_USER

    # send customer the receipt
    send_mail(
        subject = 'Your ordered items',
        message = f'''
            Thank you for shopping at AiAi Market. Here is your receipt:
            \nReceipt ID: {receipt.id}{receipt.checkout_summary}
        ''',
        recipient_list = [address.email],
        from_email = email_from
    )

    receipt.receipt_sent_date = timezone.now()
    receipt.sent = True
    receipt.save()

    context['receipt_id']= receipt.id
    context['customer'] = receipt.customer.username
    context['orders'] = receipt.checkout.order.all()

    for order in orders:
        order.open = False
        order.save()
    checkout_obj.open = False
    checkout_obj.checkout_date = timezone.now()
    checkout_obj.save()
    return render(request, 'products/payment_success.html', context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)
    
    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )
        print(session)
    return HttpResponse(status=200)


def order_history_view(request):
    user = request.user
    receipts = CheckoutReceipt.objects.filter(customer=user)
    context= {'receipts': receipts}
    return render(request, 'products/receipts.html', context)