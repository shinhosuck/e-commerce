
from .models import ShippingAddress
from django import forms 



class ProductReviewForm(forms.Form):
    rating = forms.CharField(max_length=5)
    title = forms.CharField(max_length=100)
    content = forms.CharField(widget=forms.Textarea)


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
