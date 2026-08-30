from rest_framework import serializers
from .models import Customer
from users.serializers import UserSerializer


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Customer
        fields = ['user', 'city', 'address', 'notes', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
