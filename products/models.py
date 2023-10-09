from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
import uuid
from decimal import Decimal
from django.utils import timezone


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images')

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Product Categories'


class ProductSubCategory(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Product Sub-categories'
        ordering = ['category']


class Product(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    seller_organization = models.CharField(max_length=50)
    product_image = models.ImageField(upload_to='product_image')
    description = models.CharField(max_length=100)
    detail = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_str_format = models.CharField(max_length=1000, null=True, blank=True)
    discount_price_str_format = models.CharField(max_length=1000, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    num_of_times_solid = models.IntegerField(default=0)
    likes = models.DecimalField(max_digits=5, decimal_places=1 ,default=0.0)

    def __str__(self):
        return self.name
    
    def save(self, *arg, **kwarg):
        price = str(self.price)
        self.price_str_format = f'{price[0:-6]},{price[-6:]}'
        super().save(*arg, **kwarg)

    def get_product_image_url(self):
        return self.product_image.url
    
    def get_absolute_url(self):
        return reverse('products:product-detail', args=[str(self.id)])
    
    def get_discount_price(self):
        sub_cat = ['High-end', 'Entry-level']
        item = Product.objects.get(id=self.id)
        if item.sub_category:
            if item.sub_category.name in sub_cat:
                discount = round(item.price - (item.price * Decimal(.10)), 2)
                for char in str(discount):
                    if char == '.':
                        index = str(discount).index(char)
                        discount = f'{str(discount)[0 : index - 3]},{str(discount)[index - 3 : index  + 3]} '
                self.discount_price_str_format = discount
                return discount
        # return 0
    
    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Products'


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return f'{self.product}'

    class Meta:
        verbose_name_plural = 'Product Images'


class ProductReview(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.IntegerField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name
    
    def calculate_rating(self):
        reviews = ProductReview.objects.filter(product__id = self.product.id)
        total_reviews = reviews.count()
        added_review = sum([review.rating for review in reviews])
        rating_average = (added_review / ( total_reviews * 5)) * 5
        # self.product.likes = rating_average
        return rating_average
    
    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Product Reviews'


class Order(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    open = models.BooleanField(default=True)

    def get_order_total(self):
        if self.product.get_discount_price():
            order_total = round(self.quantity * Decimal(self.product.get_discount_price().replace(',', '')), 2)
            return order_total
        else:
            order_total = round(self.quantity * self.product.price, 2)
            return order_total
    
    def __str__(self):
        return f'{self.customer.username} - {self.product.name}'
    
    class Meta:
        ordering = ['-open']
    

class Checkout(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ManyToManyField(Order)
    date_created = models.DateTimeField(auto_now_add=True)
    checkout_date = models.DateTimeField(null=True)
    total_amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    open = models.BooleanField(default=True)

    def set_amount_due(self):
        customer = User.objects.get(username=self.customer.username)
        checkout = Checkout.objects.get(customer=customer, open=True)
        amount_due = [product.get_order_total() for product in checkout.order.all()]
        self.total_amount_due = round(sum(amount_due), 2)
        checkout.save()
        return round(sum(amount_due), 2)
    
    def __str__(self):
        return f'{self.customer.username} - {self.order}'
    
    class Meta:
        ordering = ['-open']


class ShippingAddress(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length= 100)
    email = models.EmailField(max_length=100)
    phone_number = models.IntegerField()
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    zip_code = models.IntegerField()

    def __str__(self):
        return f'{self.customer.username}'
    
    class Meta:
        verbose_name_plural = 'Addresses'


class CheckoutReceipt(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    checkout = models.ForeignKey(Checkout, on_delete=models.PROTECT)
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    checkout_summary = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    receipt_sent_date = models.DateTimeField(null=True)
    sent = models.BooleanField(default=False)
    saving = models.CharField(max_length=100, null=True, blank=True, default='None')
    sub_total = models.CharField(max_length=100, null=True, blank=True)
    tax = models.CharField(max_length=100, null=True, blank=True)
    total = models.CharField(max_length=100, null=True, blank=True)



    def __str__(self):
        return self.customer.username
    
    class Meta:
        ordering = ['-receipt_sent_date']
        verbose_name_plural = 'Checkout Receipts'