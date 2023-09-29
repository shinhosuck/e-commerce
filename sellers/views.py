from django.shortcuts import render
from django.http import HttpResponse




def seller_view(request):
    return render(request, 'sellers/seller.html', context=None)
