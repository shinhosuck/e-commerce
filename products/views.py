from django.shortcuts import render, redirect, get_list_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils import timezone
from .context_processors import get_basket_total, create_checkout_summary
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
from django.template.loader import render_to_string, get_template
from django.conf import settings
import stripe
import json
from decimal import Decimal
from sellers.models import SellerSignUp
import random
from django.core.files import File
import uuid


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
    user = request.user
    query_set = Product.objects.all()
    popular = [obj for obj in query_set if obj.num_of_times_solid >= 5]
    for_you = []
    
    if not user.is_authenticated or not user.order_set.all():
        for_you = random.sample(list(query_set), len(query_set))
        print('FOR YOU:', for_you)
    else:
        categories = set(obj.product.category.name for obj in user.order_set.all())
        for category in categories:
            objs = query_set.filter(category__name__iexact=category)
            for_you += list(objs)
        for_you = random.sample(for_you, len(for_you))
    
    context = {
        'latest': query_set[0:6], 
        'popular':popular[0:6], 
        'for_you':for_you[0:6]
    }

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

    try:
        request.user.sellersignup
    except Exception as e:
        messages.error(request, f'{e}. Please sign up to sell on AiAi Market')
        return redirect('sellers:seller-signup')
    
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
    
    sort_by_price = ''
    str_list = q.lower().split('_')

    if 'sort' in str_list:
        sort_by_price = ' '.join(str_list[-1].split('-'))
        q = str_list[0]

    context = {
        'q': q.capitalize(),
        'sort_by': sort_by_price.capitalize()
    }

    # Search by Category, sub-category, and product name
    query_set = Product.objects.filter(Q(category__name__icontains = q) | 
            Q(sub_category__name__icontains = q) | Q(name__icontains = q))
    if sort_by_price == 'price low to high':
        context['query_set'] = query_set.order_by('price')
    elif sort_by_price == 'price high to low':
        context['query_set'] = query_set.order_by('-price')
    else:
        context['query_set'] = query_set

    return render(request, 'products/search_result.html', context)


def deals_and_sales_view(request):
    string = request.GET.get('str')

    category = ''
    sort_by_price = ''

    str_list = string.lower().split(' ')

    if 'sort' in str_list:
        index = str_list.index('sort')
        sort_by_price = ' '.join(str_list[index+1:])
        string= ' '.join(str_list[0:index])
    elif 'category' in str_list:
        string = ' '.join(str_list[1:])
        category = str_list[0]

    context = {
        'string': string.capitalize(),
        'sort_by': sort_by_price.capitalize()
    }

    # latest, most poplura, just for you
    # sort price by low to high and high to low
    if string.lower() == 'latest product':
        query_set = Product.objects.all()
        if sort_by_price == 'price low to high':
            context['query_set'] = query_set.order_by('price')
        elif sort_by_price == 'price high to low':
            context['query_set'] = query_set.order_by('-price')
        else:
            context['query_set'] = query_set

    elif string.lower() == 'most popular':
        query_set = [item for item in Product.objects.all() if item.num_of_times_solid >= 5]
        new_objs = Product.objects.filter(id__in=[item.id for item in query_set])
        if sort_by_price == 'price low to high':
            context['query_set'] = new_objs.order_by('price')
        elif sort_by_price == 'price high to low':
            context['query_set'] = new_objs.order_by('-price')
        else:
            context['query_set'] = query_set

    elif string.lower() == 'just for you':
        user = request.user
        query_set = []
        have_ordered = []
        if not user.is_authenticated or not user.order_set.all():
            have_ordered = set(product.category.name for product in Product.objects.all())
        else:
            have_ordered = set(item.product.category.name for item in Order.objects.filter(customer=user))
        for category in have_ordered:
            items = [query_set.append(item) for item in Product.objects.filter(category__name__iexact = category)]
            new_objs = Product.objects.filter(id__in=[item.id for item in query_set])
            if sort_by_price == 'price low to high':
                context['query_set'] = new_objs.order_by('price')
            elif sort_by_price == 'price high to low':
                context['query_set'] = new_objs.order_by('-price')
            else:
                context['query_set'] = query_set

    elif string.lower() == 'up to 10% off laptop':
        query_set = [obj for obj in Product.objects.filter(category__name__iexact = 'laptop') if obj.get_discount_price()]
        query_set = Product.objects.filter(id__in=[item.id for item in query_set])
        if sort_by_price == 'price low to high':
            context['query_set'] = query_set.order_by('price')
        elif sort_by_price == 'price high to low':
            context['query_set'] = query_set.order_by('-price')
        else:
            context['query_set'] = query_set

    elif string.lower() == 'up to 10% off desktop pc':
        query_set = [obj for obj in Product.objects.filter(category__name__iexact = 'desktop pc') if obj.get_discount_price()]
        query_set = Product.objects.filter(id__in=[item.id for item in query_set])
        if sort_by_price == 'price low to high':
            context['query_set'] = query_set.order_by('price')
        elif sort_by_price == 'price high to low':
            context['query_set'] = query_set.order_by('-price')
        else:
            context['query_set'] = query_set

    else:
        # Category
        query_set = Product.objects.filter(Q(category__name__icontains = string) | 
                Q(sub_category__name__icontains = string) | Q(name__icontains = string))
        if sort_by_price == 'price low to high':
            context['query_set'] = query_set.order_by('price')
        elif sort_by_price == 'price high to low':
            context['query_set'] = query_set.order_by('-price')
        else:
            context['query_set'] = query_set

    return render(request, 'products/deals_and_sales.html', context)


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
    return render(request, 'products/basket.html', context)


@login_required
def update_basket_view(request, id):
    user = request.user
    qty = request.GET.get('amount')
    order = Order.objects.get(customer=user, product__id=id, open=True)

    print('ORDER QUANTITY:', order.quantity)

    if order.quantity == int(qty):
        order.delete()
        messages.success(request, f'{order.product.name} has been deleted from your basket.')
        return redirect('products:product-basket')
    
    order.quantity = int(qty)
    order.save()
    messages.success(request, f'{order.product.name} quantity has been updated.')
    return redirect('products:product-basket')


@login_required
def customer_address_view(request):
    user = request.user
    orders = user.order_set.filter(open=True) 
    instance = ShippingAddress.objects.filter(customer=request.user).first()
    form = ShippingAddressForm(instance=instance)
    context = {
        'form': form,
        'orders': orders
    }

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=instance)
        if form.is_valid():
            shipping_address = form.save()
            shipping_address.customer = user
            shipping_address.save()
            if user.order_set.all():
                return redirect('products:checkout-summary')
            else:
                messages.info(request, 'Your address has been saved.')
                return redirect('products:product-list')
        else:
            context['form'] = form
    return render(request, 'products/address.html', context)


@login_required 
def checkout_summary_view(request):
    user = request.user
    query_set = Order.objects.filter(customer=user, open=True)
    address = user.shippingaddress_set.all().first()


    if not query_set.exists():
        messages.error(request, 'You basket is empty. Please add a product to your basket and try again.')
        return redirect('products:product-basket')
    if not address:
        messages.warning(request, f'{user.username}, please add your shipping address!')
        return redirect('products:shipping-address')
   
    
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

    DOMAIN = f'http://{request.get_host()}/'

    try:
        checkout_obj = Checkout.objects.get(id=id, open=True)
    except:
        messages.error(request, 'You do not have any pending orders.')
        return redirect('products:product-list')
    
    total = get_basket_total(request)['total'].replace(',','')
    total = int(Decimal(total)*100)

    checkout_session = stripe.checkout.Session.create(
        line_items=[{ 
                'price_data': { 
                    'currency': 'php', 
                    'unit_amount': f'{total}',
                    'product_data':{ 
                        'name': 'Total Amount Due'
                        }, 
                },
                'quantity': 1
            }],
        mode='payment',
        success_url = DOMAIN + f'payment/success/{id}/',
        cancel_url = DOMAIN + 'payment/cancel/',
    )
    return redirect(checkout_session.url, code=303)


@login_required
def payment_cancel_view(request):
    return render(request, 'products/payment_cancel.html')


@login_required
def payment_success_view(request, id):

    DOMAIN = f'http://{request.get_host()}/'

    customer = request.user
    orders = customer.order_set.filter(open=True)
    checkout_obj = Checkout.objects.filter(id=id, open=True).first()

    context = {
        'domain': DOMAIN,
        'basket_total': get_basket_total(request) # from context processors,
    }

    discount_amount = []
    order_total = []

    if not orders.exists() and not checkout_obj:
        messages.info(request, 'You do not have pending payment')
        return redirect('products:order-history')
    
    for item in checkout_obj.order.all():
        if item.product.get_discount_price():
            discount = item.product.price - Decimal(item.product.get_discount_price().replace(',',''))
            discount_amount.append({'id':item.product.id, 'discount':f'{discount*item.quantity:,.2f}'})
            order_total.append({'id':item.id, 'total':f'{item.get_order_total():,.2f}'})
        else:
            order_total.append({'id':item.id, 'total':f'{item.get_order_total():,.2f}'})

    # create CheckoutReceipt
    receipt = CheckoutReceipt.objects.create(
        checkout=checkout_obj, 
        customer=customer, 
        saving = '{0}'.format(get_basket_total(request)['discount_amount']),
        sub_total = '{0},{1}'.format(str(checkout_obj.set_amount_due())[0:-6], str(checkout_obj.set_amount_due())[-6:]),
        tax = '{0}'.format(get_basket_total(request)['vat']),
        total = '{0}'.format(get_basket_total(request)['total'])
    )

    address = ShippingAddress.objects.get(customer=request.user)
    email_from = settings.EMAIL_HOST_USER

    # send customer the url of the receipt
    send_mail(
        subject = 'Order cofirmation from aiai e-market',
        message = f'''
            Thank you for shopping at aiai e-market!
            click url to download your receipt: {DOMAIN}email/receipt/{receipt.id}
        ''',
        recipient_list = [address.email],
        from_email = email_from,
    )

    receipt.receipt_sent_date = timezone.now()
    receipt.sent = True
    receipt.save()

    context['discount_amount'] = discount_amount
    context['order_total'] = order_total
    context['receipt_id']= receipt.id
    context['customer'] = receipt.customer
    context['orders'] = receipt.checkout.order.all()
    context['email'] = address.email
    context['order_date'] = receipt.created

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


@login_required
def order_history_view(request):
    user = request.user
    receipts = CheckoutReceipt.objects.filter(customer=user)

    context= {'receipts': receipts}
    order_total = []

    for receipt in receipts:
        if not receipt.checkout_summary:
            address = ShippingAddress.objects.get(customer=user)
            full_name = f'{address.first_name} {address.last_name}'
            media_root = settings.MEDIA_ROOT
            id = uuid.uuid4()

            saving = ''
            if not receipt.saving or receipt.saving == '[]':
                saving = 'n/a'
            else:
                saving = receipt.saving
            
            receipt_id = receipt.id
            customer = full_name
            saving = saving
            sub_total = receipt.sub_total
            tax = receipt.tax 
            total = receipt.total

            with open(f'{media_root}/checkout_summary/checkout_summary-{id}.txt', 'w') as f:
                file = File(f)
                file.write(f'ID: {receipt_id}\nCustomer: {customer}\nSaving: {saving}\nSub-total: {sub_total}\nTax: {tax}\nTotal: {total}')
                receipt.checkout_summary = f'/checkout_summary/checkout_summary-{id}.txt'
                receipt.save()

        orders = receipt.checkout.order.all()

        for order in orders:
            order_total.append({'id':order.product.id, 'total':f'{order.get_order_total():,.2f}'})
    context['order_total'] = order_total
    return render(request, 'products/order_history.html', context)


def email_receipt_view(request, id):

    result = create_checkout_summary(request, receipt_id=id)

    if result:
        error = result['error']
        if error:
            messages.error(request, f'{error}')
            return redirect('products:product-list')

    try:
        receipt = CheckoutReceipt.objects.get(id=id)
    except Exception as e:
        messages.error(request, f'{e}')
        return redirect('products:product-list')

    order_total = [{'id':order.id, 'total':f'{order.get_order_total():,.2f}'} for order in receipt.checkout.order.all()]
    sub_total = f'{receipt.checkout.total_amount_due:,.2f}'
    vat = f'{float(receipt.checkout.total_amount_due)*.12:,.2f}'
    total = f"{Decimal(sub_total.replace(',','')) + Decimal(vat.replace(',','')):,.2f}"
    discount_total = []

    for order in receipt.checkout.order.all():
        if order.product.get_discount_price():
            discount = (order.product.price - Decimal(order.product.get_discount_price().replace(',',''))) * order.quantity
            discount_total.append(discount)

    context = {
        'discount_total': f'{sum(discount_total):,}',
        'orders':receipt.checkout.order.all(),
        'order_total': order_total,
        'sub_total': sub_total,
        'vat': vat,
        'total': total,
        'customer': receipt.customer,
        'receipt_id': id,
        'date': receipt.created,
        'receipt': receipt
    }
    
    # html_template = 'products/email_receipt.html'

    # html_message = render_to_string(html_template, context)
    # plain_message = strip_tags(html_message)
    # address = ShippingAddress.objects.filter(customer=receipt.customer).first()
    # email_from = settings.EMAIL_HOST_USER

    # message = EmailMultiAlternatives(
    #     subject = 'Your order',
    #     body = plain_message,
    #     from_email = email_from,
    #     to = [address.email],
    # )
    # message.attach_alternative(html_message, 'text/html')
    # message.send()

    # messages.info(request, f'Copy of receipt has been sent to your email account {address.email}')
    return render(request, 'products/email_receipt.html', context)
