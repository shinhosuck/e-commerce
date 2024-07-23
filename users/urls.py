from django.urls import path 
from .views import (
    register_view, 
    login_view,
    logout_view,
    profile_view,
    message_view
)


app_name = 'users'


urlpatterns = [
    path('register/', register_view, name='user-register'),
    path('login/', login_view, name='user-login'),
    path('logout/', logout_view, name='user-logout'),
    path('user/profile/', profile_view, name='user-profile'),
    path('message/', message_view, name='user-message')
]
