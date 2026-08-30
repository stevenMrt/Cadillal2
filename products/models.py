from django.db import models
from categories.models import Category


class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
    )

    name = models.CharField(max_length=150)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=0)
    unit = models.CharField(max_length=20, default='unidad')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    images = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
