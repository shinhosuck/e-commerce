from django.shortcuts import render, redirect
from .forms import (
    SellerSignUpForm,
    CreateProductForm, 
    CreateProductImageForm
)
from products.models import SubCategory, ProductImage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json


@login_required
def seller_register_view(request):
    user = request.user

    try:
        seller_exists = user.seller
    except Exception as e:
        form = SellerSignUpForm()

        context = {
            'form': form
        }
        
        if request.method == 'POST':
            form = SellerSignUpForm(request.POST)
            if form.is_valid():
                new_seller = form.save(commit=False)
                new_seller.seller_name = user
                new_seller.save()
                messages.success(request, 'Seller account successfully created!')
                return redirect('sellers:product-create')
            else:
                context['form'] = form
        return render(request, 'sellers/seller.html', context)
    
    if seller_exists:
        messages.info(request, 'You have already signed up to sell on aiai.')
        return redirect('sellers:product-create')


@login_required()
def product_create_view(request):
    try:
        seller = request.user.seller
    except Exception as e:
        messages.error(request, f'{e}. Please sign up to sell on AiAi Market')
        return redirect('sellers:seller-signup')
    
    query_set = SubCategory.objects.all()
    category_name = []
    sub_categories = []

    for obj in query_set:
        if obj.category.name not in category_name:
            category_name.append(obj.category.name)
            sub_categories.append(
                {
                    'id':obj.category.id ,
                    'category_name':obj.category.name, 
                    'sub_categories':[{'id':obj.id, 'name':obj.name}]
                }
            )
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
        product.seller = seller.seller_name.username
        product.save()
        return redirect('products:product-detail', product.id)
    return render(request, 'sellers/product_create.html', context)
