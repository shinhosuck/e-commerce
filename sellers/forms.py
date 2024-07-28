from .models import Seller
from django.forms import ClearableFileInput
from products.models import Product, ProductImage
from django import forms 



class SellerSignUpForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'email',
            'address',
            'city',
            'state',
            'province',
            'postal_code',
        ]

class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = [
            'category',
            'sub_category',
            'name',
            'brand',
            'detail', 
            'price', 
            'available'
        ]


class CreateProductImageForm(forms.ModelForm):
    allow_multiple_selected = True
    class Meta:
        model = ProductImage
        fields = ['image']

        labels = {
            'image': 'Product Images'
        }

        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }