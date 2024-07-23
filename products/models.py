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
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='sub_categories')
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
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE, related_name='sub_cat_products')
    name = models.CharField(max_length=50)
    slug = models.SlugField(null=True, blank=True, unique=True)
    brand = models.CharField(max_length=50)
    seller = models.CharField(max_length=50)
    image = models.ImageField(upload_to='product_image')
    detail = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    available = models.BooleanField(default=True)
    quantity_sold = models.IntegerField(default=0)
    likes = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    def __str__(self):
        return self.name
    
    def get_product_image_url(self):
        return self.image.url
    
    def get_absolute_url(self):
        return reverse('products:product-detail', args=[str(self.id)])
    
    def get_discount_price(self):
        sub_cat = ['High-end', 'Entry-level']
        product = Product.objects.get(id=self.id)
        if product.sub_category:
            if product.sub_category.name in sub_cat:
                discount = f'{product.price - (product.price * Decimal(.10)):,.2f}'
                return discount
        return None
    
    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Products'


class ProductImage(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return f'{self.product}'

    class Meta:
        verbose_name_plural = 'Product Images'


class Review(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_reviews')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=100)
    content = models.TextField()
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.name
    
    def calculate_rating(self):
        reviews = Review.objects.filter(product__id = self.product.id)
        total_reviews = reviews.count()
        added_review = sum([review.rating for review in reviews])
        rating_average = (added_review / ( total_reviews * 5)) * 5
        return rating_average
    
    class Meta:
        ordering = ['-created']
        verbose_name_plural = 'Product Reviews'


class Cart(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_date = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField(default=1)
    open = models.BooleanField(default=True)

    def get_order_total(self):
        order_total = None
        if self.product.get_discount_price():
            order_total = round(self.quantity * Decimal(self.product.get_discount_price().replace(',', '')), 2)
        else:
            order_total = round(self.quantity * self.product.price, 2)
        return f'{order_total:,}'
    
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
    order = models.ManyToManyField(Cart)
    date_created = models.DateTimeField(auto_now_add=True)
    checkout_date = models.DateTimeField(null=True)
    total_amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    open = models.BooleanField(default=True)

    def set_amount_due(self, id=None):
        user = User.objects.get(id=self.customer.id)
        try:
            checkout = Checkout.objects.get(customer=user, open=True)
        except Checkout.DoesNotExist:
            checkout = Checkout.objects.get(id=id)
        amount_due = [Decimal(order.get_order_total().replace(',', '')) for order in checkout.order.all()]
        self.total_amount_due = round(sum(amount_due), 2)
        checkout.save()
        return f'{round(sum(amount_due), 2):,}'
    
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
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
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


class Receipt(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    checkout = models.ForeignKey(Checkout, on_delete=models.PROTECT)
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    receipt_sent_date = models.DateTimeField(null=True)
    sent = models.BooleanField(default=False)
    saving = models.CharField(max_length=100, blank=True, null=True)
    sub_total = models.CharField(max_length=100, null=True, blank=True)
    tax = models.CharField(max_length=100, null=True, blank=True)
    total = models.CharField(max_length=100, null=True, blank=True)
    checkout_summary = models.FileField(upload_to='checkout_summary', null=True, blank=True)


    def __str__(self):
        return self.customer.username
    

    class Meta:
        ordering = ['-receipt_sent_date']
        verbose_name_plural = 'Receipts'