from django.contrib import admin
from .models import SellerSignUp 




class SellerSignUpAdmin(admin.ModelAdmin):
    list_display = ['member_name', 'organization_name', 'created', 'updated']
    
admin.site.register(SellerSignUp, SellerSignUpAdmin)
