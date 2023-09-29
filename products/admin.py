from django.contrib import admin
from .models import (
    ProductCategory, 
    Product, 
    ProductImage,
    ProductReview,
    ProductSubCategory,
    Order,
    Checkout,
    ShippingAddress,
    CheckoutReceipt
)



class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register( ProductCategory, ProductCategoryAdmin)


class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']

admin.site.register(ProductSubCategory, ProductSubCategoryAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'category', 'sub_category', 'created', 'updated', 'available']
    search_fields = ['name', 'category__name', 'sub_category__name']

admin.site.register(Product, ProductAdmin)


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product']
    search_fields = ['product__name']

admin.site.register(ProductImage, ProductImageAdmin)


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'rating', 'created', 'updated']

admin.site.register(ProductReview, ProductReviewAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'open', 'quantity', 'ordered_date']

admin.site.register(Order, OrderAdmin)


class CheckoutAdmin(admin.ModelAdmin):
    list_display = ['customer', 'total_amount_due', 'open', 'date_created', 'checkout_date']

admin.site.register(Checkout, CheckoutAdmin)


class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'first_name', 'last_name']

admin.site.register(ShippingAddress, ShippingAddressAdmin)

class CheckoutReceiptAdmin(admin.ModelAdmin):
    list_display = ['customer', 'sent', 'receipt_sent_date', 'created']

admin.site.register(CheckoutReceipt, CheckoutReceiptAdmin)