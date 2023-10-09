from django.urls import path 
from .views import seller_view


app_name = 'sellers'



urlpatterns = [
    path('seller/', seller_view, name='sellers-seller')
]