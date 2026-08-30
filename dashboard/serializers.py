from rest_framework import serializers


class DashboardSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    total_sales = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_products = serializers.IntegerField()
    total_users = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    recent_orders = serializers.ListField()
