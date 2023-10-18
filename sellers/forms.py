from .models import SellerSignUp
from django import forms 



class SellerSignUpForm(forms.ModelForm):
    class Meta:
        model = SellerSignUp
        fields = [
            'organization_name',
            'phone_number',
            'email',
            'address',
            'city',
            'state',
            'province',
            'country',
            'postal_code',
        ]