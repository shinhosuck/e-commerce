from .models import Product, ProductImage, ProductReview, ShippingAddress
from django.forms import ClearableFileInput
from django import forms 




class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Product 
        fields = [
            'category',
            'sub_category',
            'name',
            'brand',
            'seller_organization',
            'product_image',
            'description', 
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
            'image': 'Additional Product Images'
        }
        widgets = {
            'image': ClearableFileInput(attrs={'multiple': True}),
        }


class ProductReviewForm(forms.Form):
    rating = forms.CharField(max_length=5)
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea, required=False)


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'address', 
            'city', 
            'province',
            'state',
            'zip_code'
        ]
