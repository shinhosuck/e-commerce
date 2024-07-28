from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from products.models import Product
import uuid


class Seller(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    seller_name = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.seller_name.username}'


class SellerProduct(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seller_products')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product.name}'

