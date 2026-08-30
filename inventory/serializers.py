from rest_framework import serializers
from .models import InventoryMovement


class InventoryMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryMovement
        fields = ['id', 'product', 'movement_type', 'quantity', 'previous_stock', 'new_stock', 'reason', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, attrs):
        movement_type = attrs.get('movement_type')
        quantity = attrs.get('quantity')
        previous_stock = attrs.get('previous_stock')
        new_stock = attrs.get('new_stock')

        if previous_stock is None or new_stock is None:
            return attrs

        expected = previous_stock + quantity if movement_type == 'in' else previous_stock - quantity
        if new_stock != expected:
            raise serializers.ValidationError(
                f'Inconsistencia de stock: previous_stock ({previous_stock}) + quantity ({quantity}) != new_stock ({new_stock}) para movimiento tipo {movement_type}.'
            )

        if new_stock < 0:
            raise serializers.ValidationError('El stock resultante no puede ser negativo.')

        return attrs

    def create(self, validated_data):
        product = validated_data.get('product')
        movement_type = validated_data.get('movement_type')
        quantity = validated_data.get('quantity')

        if product and movement_type in ('in', 'out') and validated_data.get('previous_stock') is None:
            validated_data['previous_stock'] = product.stock
            if movement_type == 'in':
                validated_data['new_stock'] = product.stock + quantity
            else:
                validated_data['new_stock'] = product.stock - quantity

        return super().create(validated_data)
