from django.contrib import admin
from .models import UserProfile, Message




class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'email']
    search_fields = ['user', 'first_name', 'last_name', 'email', 'user__id']

admin.site.register(UserProfile, UserProfileAdmin)


class MessageAdmin(admin.ModelAdmin):
    list_display = ['user', 'username', 'email', 'created']

admin.site.register(Message, MessageAdmin)
