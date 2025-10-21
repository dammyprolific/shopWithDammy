from django.db import models
from django.utils.text import slugify
from django.conf import settings
from cloudinary.models import CloudinaryField

class Products(models.Model):
    CATEGORY = [
        ("ELECTRONICS", "Electronics"),
        ("GROCERIES", "Groceries"),
        ("CLOTHINGS", "Clothings"),
        ("CARS", "Cars"),
        ("ACCESSORY", "Accessory"),
        ("PHONES", "Phones"),
        ("OTHERS", "Others"),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=15, choices=CATEGORY, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            while Products.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    @property
    def formatted_price(self):
        return "{:,.2f}".format(self.price)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Products, on_delete=models.CASCADE, related_name='extra_images'
    )
    image = models.ImageField(upload_to='img/extra/')

    def __str__(self):
        return f"Extra Image for {self.product.name}"


class Cart(models.Model):
    cart_code = models.CharField(max_length=11, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cart_code


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart {self.cart.id}"


class Transaction(models.Model):
    ref = models.CharField(max_length=225, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='NGN')
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction {self.ref} - {self.status}"

    @property
    def formatted_amount(self):
        """Returns amount with comma formatting, e.g., 67,000,000.00"""
        return "{:,.2f}".format(self.amount)
