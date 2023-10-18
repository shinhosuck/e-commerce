from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
import uuid


class SellerSignUp(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    member_name = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    organization_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    country = CountryField()
    postal_code = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.member_name.username}'



