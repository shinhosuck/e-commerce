from django.urls import path 
from .views import seller_sign_up_view


app_name = 'sellers'



urlpatterns = [
    path('seller/', seller_sign_up_view, name='seller-signup')
]