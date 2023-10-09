from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages



def user_register_view(request):
    user = request.user
    if user.is_authenticated:
        messages.info(request, f'Your are already registered and logged in.')
        return redirect('products:product-list')
    
    form = UserCreationForm()
    context = {'form': form}

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Username "{user.username}" has been suucessfully registered.')
            return redirect('users:user-login')
        else:
            context['form'] = form
            print(form.error_messages)
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