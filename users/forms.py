from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms




class UserEmailForm(forms.Form):
    email = forms.EmailField(max_length=200 ,widget=forms.EmailInput(attrs={'required':True}))
        