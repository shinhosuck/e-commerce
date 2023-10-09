from django.contrib import admin
from .models import UserProfile




class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email']
    search_fields = ['user', 'first_name', 'last_name', 'email', 'user__id']

admin.site.register(UserProfile, UserProfileAdmin)
