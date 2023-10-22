from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

from .models import UserProfile, Message


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile 
        fields = ['first_name', 'last_name', 'profile_image', 'email']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User 
        fields = ['username']

class UserEmailForm(forms.Form):
    email = forms.EmailField(max_length=200 ,widget=forms.EmailInput(attrs={'required':True}))


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['username', 'email', 'message']
