from django.db import models

# Create your models here.
from django.db import models
from Accounts.models import User
from django import forms
from pc_build.models import Components

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    shop_name = models.CharField(max_length=255)
    owner_name = models.CharField(max_length=255)

    phone = models.CharField(max_length=15)
    email = models.EmailField()

    address = models.TextField()
    city = models.CharField(max_length=100)

    profile_image = models.ImageField(upload_to='vendors/', blank=True, null=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name

class InventoryItem(models.Model):
    vendor = models.ForeignKey('Vendors.Vendor', on_delete=models.CASCADE, related_name='inventory') # Adjust path if Vendor is in a different app
    component = models.ForeignKey(Components, on_delete=models.CASCADE, related_name='vendor_listings')
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('vendor', 'component')

    def __str__(self):
        return f"{self.vendor.shop_name} | {self.component.name} - ${self.price}"