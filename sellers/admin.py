from django.contrib import admin
from .models import Seller, SellerProduct




class SellerAdmin(admin.ModelAdmin):
    list_display = ['seller_name', 'first_name', 'last_name', 'created', 'updated']
    
admin.site.register(Seller, SellerAdmin)


class SellerProductAdmin(admin.ModelAdmin):
    list_display = ['product', 'seller', 'created']
    
admin.site.register(SellerProduct, SellerProductAdmin)

