from rest_framework import generics, permissions
from .models import Customer
from .serializers import CustomerSerializer
from users.permissions import IsAdmin


class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class CustomerDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
