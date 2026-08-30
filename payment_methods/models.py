from django.db import models
from users.models import User


class PaymentMethod(models.Model):
    TYPE_CHOICES = (
        ('credit_card', 'Tarjeta de crédito'),
        ('debit_card', 'Tarjeta de débito'),
        ('bank', 'Cuenta bancaria'),
        ('nequi', 'Nequi'),
        ('other', 'Otro'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    last_four = models.CharField(max_length=4, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)
    holder_name = models.CharField(max_length=150)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_display()} **** {self.last_four} - {self.user.username}"
