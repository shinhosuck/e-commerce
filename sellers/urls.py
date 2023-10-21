from django.urls import path 
from .views import seller_register_view


app_name = 'sellers'



urlpatterns = [
    path('seller/register/', seller_register_view, name='seller-register')
]