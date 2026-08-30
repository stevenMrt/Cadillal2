from django.db import models
from orders.models import Order
from users.models import User


class Sale(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('partially_paid', 'Parcial'),
        ('refunded', 'Reembolsado'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='sale')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, default='other')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Venta #{self.id} - Pedido #{self.order.id}"
