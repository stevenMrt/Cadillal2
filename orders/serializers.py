from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem
from payment_methods.models import PaymentMethod
from products.models import Product
from inventory.models import InventoryMovement


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'quantity', 'unit_price', 'discount', 'tax', 'subtotal']
        read_only_fields = ['id']


class PaymentMethodField(serializers.Field):
    def to_representation(self, value):
        return value.type if value else None

    def to_internal_value(self, data):
        if not data:
            return None
        mapped = data
        if mapped == 'cash':
            mapped = 'other'
        elif mapped == 'card':
            mapped = 'credit_card'
        elif mapped == 'transfer':
            mapped = 'other'
        try:
            return PaymentMethod.objects.get(type=mapped)
        except PaymentMethod.DoesNotExist:
            return None


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    payment_method_display = serializers.CharField(source='payment_method.type', read_only=True)
    payment_method = PaymentMethodField(required=False, allow_null=True)

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'status', 'payment_status', 'payment_method', 'payment_method_display',
            'notes', 'subtotal', 'discount', 'tax', 'shipping', 'total',
            'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'created_at', 'updated_at']

    def validate_items(self, items):
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            if product_id:
                try:
                    product = Product.objects.get(id=product_id)
                except Product.DoesNotExist:
                    raise serializers.ValidationError(f'Producto {product_id} no existe')
                if product.status != 'active':
                    raise serializers.ValidationError(f'Producto {product.name} no está disponible')
                if product.stock < quantity:
                    raise serializers.ValidationError(f'Stock insuficiente para {product.name}. Disponible: {product.stock}')
        return items

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        items_data = validated_data.pop('items')
        payment_method = validated_data.pop('payment_method', None)

        with transaction.atomic():
            order = Order.objects.create(payment_method=payment_method, **validated_data)
            for item_data in items_data:
                product_id = item_data.get('product_id')
                if product_id:
                    product = Product.objects.select_for_update().get(id=product_id)
                    quantity = item_data['quantity']
                    if product.stock < quantity:
                        raise serializers.ValidationError(f'Stock insuficiente para {product.name}. Disponible: {product.stock}')
                    previous_stock = product.stock
                    new_stock = previous_stock - quantity
                    product.stock = new_stock
                    product.save()
                    InventoryMovement.objects.create(
                        product=product,
                        movement_type='out',
                        quantity=quantity,
                        previous_stock=previous_stock,
                        new_stock=new_stock,
                        reason=f'Venta - Pedido #{order.id}',
                    )
                OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.role != 'admin' and instance.customer_id != request.user.id:
            raise serializers.ValidationError('No tienes permiso para modificar este pedido.')

        new_status = validated_data.get('status', instance.status)
        if new_status == 'cancelled' and instance.status != 'cancelled':
            self._restore_stock(instance)

        items_data = validated_data.pop('items', None)
        payment_method = validated_data.pop('payment_method', None)
        if payment_method is not None:
            instance.payment_method = payment_method
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            with transaction.atomic():
                old_items = {item.product_id: item.quantity for item in instance.items.all() if item.product_id}
                instance.items.all().delete()
                for item_data in items_data:
                    product_id = item_data.get('product_id')
                    quantity = item_data['quantity']
                    if product_id:
                        product = Product.objects.select_for_update().get(id=product_id)
                        old_qty = old_items.get(product_id, 0)
                        new_qty = quantity - old_qty
                        if new_qty > 0 and product.stock < new_qty:
                            raise serializers.ValidationError(f'Stock insuficiente para {product.name}. Disponible: {product.stock}')
                        previous_stock = product.stock
                        new_stock = previous_stock - new_qty
                        product.stock = new_stock
                        product.save()
                        InventoryMovement.objects.create(
                            product=product,
                            movement_type='out',
                            quantity=new_qty,
                            previous_stock=previous_stock,
                            new_stock=new_stock,
                            reason=f'Actualización - Pedido #{instance.id}',
                        )
                    OrderItem.objects.create(order=instance, **item_data)
        return instance

    def _restore_stock(self, instance):
        for item in instance.items.all():
            if item.product_id:
                product = Product.objects.select_for_update().get(id=item.product_id)
                product.stock = product.stock + item.quantity
                product.save()
                InventoryMovement.objects.create(
                    product=product,
                    movement_type='in',
                    quantity=item.quantity,
                    previous_stock=product.stock - item.quantity,
                    new_stock=product.stock,
                    reason=f'Cancelación - Pedido #{instance.id}',
                )
