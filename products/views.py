from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils import timezone
from .context_processors import get_cart_total, create_checkout_summary
from .models import (
    Product, 
    ProductImage,  
    ProductCategory,
    ProductSubCategory,
    Review,
    Cart,
    Checkout,
    ShippingAddress,
    Receipt,
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
from sellers.models import SellerSignUp
from django.core.files import File
import uuid
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger
)

from django.utils.text import slugify

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET


def home_view(request):
    category = ProductCategory.objects.prefetch_related('products')
    products = None

    for cat in category:
        queryset = cat.products.all()

        if not products:
            products = list(queryset)
        else:
            for qs in queryset:
                products.append(qs)

    you_might_like = [product for product in products if product.sub_category.name == 'Entry-level']
    
    if len(you_might_like) > 4:
        remainder = len(you_might_like) % 4
        you_might_like = you_might_like[0: (len(you_might_like) - remainder)]

    context = {
        'category': category,
        'featured': products[-5:-1],
        'latest': products[0:8],
        'you_might_like': you_might_like
    }
    return render(request, 'products/home.html', context)


def product_list_view(request):
    filter = request.GET.get('filter') or None
    qs = Product.objects.all()

    if filter:
        if filter == 'Price low to high':
            qs = qs.order_by('price')
        elif filter == 'Price high to low':
            qs = qs.order_by('-price')

    paginator = Paginator(qs, 8)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products, 
        'page': page,
        'filter': filter or 'Featured'

    }
    return render(request, 'products/product_list.html', context)


def product_detail_view(request, id): 
    try:
        product = Product.objects.get(id=id)
    except Exception as e:
        messages.error(request, f'{e}')
        return redirect('products:product-home')
    
    context = {
        'product': product,
        'images': product.product_images.all(),
        'reviews': product.product_reviews.all()
    }
    return render(request, 'products/product_detail.html', context)


def shop_by_category(request, str):
    qs = Product.objects.filter(category__name=str)
    filter = request.GET.get('filter') or None

    if filter:
        if filter == 'Price low to high':
            qs = qs.order_by('price')
        elif filter == 'Price high to low':
            qs = qs.order_by('-price')

    paginator = Paginator(qs, 8)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'products': products, 
        'page': page,
        'category':str,
        'filter': filter or 'Featured'
    }
    return render(request, 'products/shop_by_category.html', context )


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
def write_review_view(request, id):
    existing_review = Review.objects.filter(id=request.GET.get('update')).first()
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
                new_review = Review.objects.create(
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
        checkouts = Checkout.objects.filter(
            customer=user, 
            order__product=product, 
            open=False
        )

        if not checkouts.exists():
            messages.error(request, 'You are not authorized to write review on this product.')
            return redirect('products:product-detail', id)
        
        elif checkouts.exists():
            purchase_verified = []
            for checkout in checkouts:
                orders = checkout.order.filter(product=product)
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


@login_required
def add_to_cart_view(request, id):
    product = Product.objects.get(id=id)
    order = Cart.objects.filter(customer=request.user ,product=product, open=True).first()
    if order:
        order.quantity += 1
        order.save()
        messages.success(request, f'{product.name} quantity has been updated.')
        return redirect('products:product-cart')
    else:
        Cart.objects.create(customer=request.user, product=product, quantity=1)
        messages.success(request, f'{product.name} has been added to the basket.')
        return redirect('products:product-cart')


@login_required
def cart_view(request):
    user = request.user
    query_set = user.orders.all().filter(open=True)
    context = {'query_set': query_set}
    return render(request, 'products/cart.html', context)


@login_required
def update_cart_view(request, id):
    user = request.user
    delete = request.GET.get('delete') or None
    qty = request.GET.get('quantity') or None
    
    order = Cart.objects.get(customer=user, product__id=id, open=True)

    if delete == 'True':
        order.delete()
        messages.success(request, f'{order.product.name} has been deleted from your basket.')
        return redirect('products:product-cart')

    if order.quantity != int(qty):
        order.quantity = qty
        order.save()

    messages.success(request, f'{order.product.name} quantity has been updated.')
    return redirect('products:product-cart')


@login_required
def customer_address_view(request):
    user = request.user
    orders = user.orders.filter(open=True) 
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
            if orders:
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
    orders = Cart.objects.filter(customer=user, open=True)
    address = user.addresses.first()

    # if not orders.exists():
    #     messages.error(request, 'You basket is empty. Please add a product to your basket and try again.')
    #     return redirect('products:product-cart')
    if not address:
        messages.warning(request, f'{user.username}, please add your shipping address!')
        return redirect('products:shipping-address')
   
    context = {'orders': orders}
    return render(request, 'products/checkout_summary.html', context)


@login_required
def checkout_view(request):
    user= request.user
    orders = Cart.objects.filter(customer=user, open=True)

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
    
    total = get_cart_total(request)['total'].replace(',','')
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
    user = request.user
    DOMAIN = f'http://{request.get_host()}/'

    address = ShippingAddress.objects.get(customer=user)
    email_from = settings.EMAIL_HOST_USER

    orders = user.orders.filter(open=True)
    checkout_obj = Checkout.objects.filter(id=id).first()

    if checkout_obj.open:
        checkout_obj.open = False
        checkout_obj.checkout_date = timezone.now()
        checkout_obj.save()

    for order in orders:
        order.open = False
        order.save()
    
    context = {
        'email': address.email
    }

    # create Receipt
    # receipt = Receipt.objects.create(
    #     checkout=checkout_obj, 
    #     customer=user, 
    #     saving = get_cart_total(request).get('discount_amount'),
    #     sub_total = checkout_obj.set_amount_due(checkout_obj.id),
    #     tax = get_cart_total(request).get('vat'),
    #     total = get_cart_total(request).get('total'),
    #     receipt_sent_date = timezone.now(),
    #     sent = True
    # )

    # send customer the url of the receipt
    
    # send_mail(
    #     subject = 'Order cofirmation from aiai e-market',
    #     message = f'''
    #         Thank you for shopping at aiai e-market!
    #         click url to download your receipt: {DOMAIN}email/receipt/{receipt.id}
    #     ''',
    #     recipient_list = [address.email],
    #     from_email = email_from,
    # )

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
    return HttpResponse(status=200)


@login_required
def order_history_view(request):
    user = request.user
    receipts = Receipt.objects.filter(customer=user)

    context= {'receipts': receipts}
    order_total = []

    for receipt in receipts:
        if not receipt.checkout_summary:
            address = ShippingAddress.objects.get(customer=user)
            full_name = f'{address.first_name} {address.last_name}'
            media_root = settings.MEDIA_ROOT
            id = uuid.uuid4()

            saving = ''
            if not receipt.saving:
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
            order_total.append({'id':order.product.id, 'total':order.get_order_total()})
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
        receipt = Receipt.objects.get(id=id)
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
    # plain_message = (html_message)
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
