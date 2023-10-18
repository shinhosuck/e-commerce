from django.shortcuts import render, redirect
from .forms import SellerSignUpForm
from .models import SellerSignUp


def seller_sign_up_view(request):

    sellers = SellerSignUp.objects.all()
    for obj in sellers:
        obj.delete()

    user = request.user
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
