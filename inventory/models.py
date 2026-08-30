from django.db import models
from django.core.exceptions import ValidationError
from products.models import Product


class InventoryMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Entrada'),
        ('out', 'Salida'),
        ('adjustment', 'Ajuste'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    previous_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} - {self.quantity}"

    def clean(self):
        expected = self.previous_stock + self.quantity if self.movement_type == 'in' else self.previous_stock - self.quantity
        if self.new_stock != expected:
            raise ValidationError(
                f'Inconsistencia de stock: previous_stock ({self.previous_stock}) + quantity ({self.quantity}) != new_stock ({self.new_stock}) para movimiento tipo {self.movement_type}.'
            )
        if self.new_stock < 0:
            raise ValidationError('El stock resultante no puede ser negativo.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
