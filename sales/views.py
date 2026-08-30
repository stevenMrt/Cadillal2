from rest_framework import generics, permissions
from .models import Sale
from .serializers import SaleSerializer
from users.permissions import IsAdmin


class SaleListCreateView(generics.ListCreateAPIView):
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return Sale.objects.select_related('order', 'customer').all()


class SaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sale.objects.select_related('order', 'customer').all()
    serializer_class = SaleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
