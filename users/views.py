from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import (
    UserProfileUpdateForm,
    UserUpdateForm,
    UserEmailForm,
    MessageForm
)
from django.contrib.auth.models import User
from .models import Message

def user_register_view(request):
    user = request.user
    if user.is_authenticated:
        messages.info(request, f'Your are already registered and logged in.')
        return redirect('products:product-list')
    
    form = UserCreationForm()
    email_form = UserEmailForm
    context = {
        'form': form,
        'email_form': email_form
    }

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Username "{user.username}" has been successfully registered.')
            return redirect('users:user-login')
        else:
            context['form'] = form
            # print(form.error_messages)
    return render(request, 'users/user_register.html', context)



def user_login_view(request):
    next = request.GET.get('next')
    print(next)
    form = AuthenticationForm(request)
    context = {'form': form}
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            messages.success(request, f'User {user} has successfully logged in.')
            login(request, user)
            if next:
                return redirect(next)
            else:
                return redirect('products:product-list')
        else:
            context['form'] = form
            login_error = form.get_invalid_login_error()
            for error in login_error:
                messages.error(request, f'{error}')
    return render(request, 'users/user_login.html', context)


def user_logout_view(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You are not logged in! Please login.')
        return redirect('products:product-list')
    else:
        if request.method == 'POST':
            logout(request)
            return redirect('users:user-login')
        return render(request, 'users/user_logout.html', context=None)


@login_required
def user_profile_view(request):
    user = request.user
    profile = user.userprofile
    profile_form = UserProfileUpdateForm(instance=profile)
    user_form = UserUpdateForm(instance=user)

    context = {
        'profile_form': profile_form,
        'user_form': user_form
    }

    if request.method == 'POST':
        profile_form = UserProfileUpdateForm(request.POST, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=user)
        if profile_form.is_valid() and user_form.is_valid():
            updated_prfile = profile_form.save()
            update_user = user_form.save()
            messages.success(request, 'Your profile have been updated successfully.')
            return redirect('products:product-list')
        else:
            context['profile_form'] = profile_form
            context['user_form'] = user_form
    return render(request, 'users/user_profile.html', context)


def message_view(request):
    query_set = Message.objects.all().delete()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save()
            try:
                user = User.objects.get(username = new_message.username)
            except Exception as e:
                messages.info(request, 'You are not member yet. Please consider joining')
                new_message.user = None
                return redirect('products:product-list')
            new_message.user = user
            messages.success(request, 'You message have been submitted successfully')
            return redirect('products:product-list')


