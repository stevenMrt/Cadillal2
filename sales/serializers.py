from rest_framework import serializers
from .models import Sale


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['id', 'order', 'customer', 'total', 'payment_method', 'payment_status', 'date']
        read_only_fields = ['id', 'date']
