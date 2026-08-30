from rest_framework import serializers
from .models import Product
from categories.models import Category


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySimpleSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category', write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'barcode', 'category', 'category_id', 'price', 'cost', 'stock', 'min_stock', 'unit', 'status', 'images', 'created_at', 'updated_at']
