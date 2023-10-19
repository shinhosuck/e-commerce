from django.shortcuts import render, redirect
from .forms import SellerSignUpForm
from .models import SellerSignUp
from django.contrib.auth.decorators import login_required


@login_required
def seller_sign_up_view(request):
    user = request.user

    try:
        seller_exists = user.sellersignup
    except Exception as e:
        form = SellerSignUpForm()

        context = {
            'form': form
        }

        if request.method == 'POST':
            form = SellerSignUpForm(request.POST)
            if form.is_valid():
                new_seller = form.save()
                new_seller.member_name = user
                new_seller.save()
                return redirect('products:product-create')
            else:
                context['form'] = form
        return render(request, 'sellers/seller.html', context)
    
    if seller_exists:
        return redirect('products:product-create')
