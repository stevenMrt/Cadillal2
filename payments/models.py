from django.db import models
from orders.models import Order
from payment_methods.models import PaymentMethod


class Payment(models.Model):
    METHOD_CHOICES = (
        ('bank', 'Bancolombia'),
        ('nequi', 'Nequi'),
        ('cash', 'Efectivo'),
        ('card', 'Tarjeta'),
        ('other', 'Otro'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('refunded', 'Reembolsado'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=100, blank=True, null=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pago #{self.id} - Pedido #{self.order.id}"
