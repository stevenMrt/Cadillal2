from django.db import models


class Category(models.Model):
    STATUS_CHOICES = (
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
    )

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
