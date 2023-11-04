from django.urls import path 
from .views import (
    user_register_view, 
    user_login_view,
    user_logout_view,
    user_profile_view,
    message_view
)


app_name = 'users'


urlpatterns = [
    path('register/', user_register_view, name='user-register'),
    path('login/', user_login_view, name='user-login'),
    path('logout/', user_logout_view, name='user-logout'),
    path('user/profile/', user_profile_view, name='user-profile'),
    path('message/', message_view, name='user-message')
]
