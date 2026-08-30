from rest_framework import serializers
from django.db.models import Sum
from django.conf import settings
from orders.models import Order
from .models import Payment


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


class PaymentSerializer(serializers.ModelSerializer):
    payment_method = PaymentMethodField(required=False, allow_null=True)
    receipt_url = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id', 'order', 'method', 'amount', 'status', 'reference', 'receipt', 'receipt_url', 'payment_method', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_receipt_url(self, obj):
        if obj.receipt and hasattr(obj.receipt, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.receipt.url)
            return settings.MEDIA_URL + obj.receipt.name
        return None

    def validate(self, attrs):
        order = attrs.get('order')
        status = attrs.get('status', self.instance.status if self.instance else 'pending')
        amount = attrs.get('amount')
        method = attrs.get('method')

        if order:
            if self.instance is None:
                user = self.context.get('request').user if self.context.get('request') else None
                if user and user.role != 'admin' and order.customer_id != user.id:
                    raise serializers.ValidationError('No tienes permiso para registrar pagos en este pedido.')

            if amount is not None and order.total is not None:
                total_paid = order.payments.exclude(pk=self.instance.pk if self.instance else None).aggregate(
                    total=Sum('amount')
                )['total'] or 0
                if status == 'paid' and (total_paid + amount) > order.total:
                    raise serializers.ValidationError('El monto del pago excede el total del pedido.')

        allowed_methods = dict(Payment.METHOD_CHOICES).keys()
        if method and method not in allowed_methods:
            raise serializers.ValidationError('Método de pago inválido.')

        receipt = attrs.get('receipt') or (self.instance.receipt if self.instance else None)
        if receipt:
            valid_types = ['image/jpeg', 'image/png', 'image/jpg', 'application/pdf']
            if receipt.content_type not in valid_types:
                raise serializers.ValidationError('Tipo de archivo no permitido. Solo JPG, PNG o PDF.')
            max_size = 5 * 1024 * 1024
            if receipt.size > max_size:
                raise serializers.ValidationError('El comprobante supera el tamaño máximo de 5MB.')

        return attrs

    def validate_status(self, value):
        if self.instance:
            current = self.instance.status
            transitions = {
                'pending': ['paid', 'failed'],
                'paid': ['refunded'],
                'failed': ['paid'],
            }
            allowed = transitions.get(current, [])
            if value not in allowed:
                raise serializers.ValidationError(f'Transición de estado inválida de {current} a {value}.')
        return value