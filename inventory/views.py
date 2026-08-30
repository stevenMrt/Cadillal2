from rest_framework import generics, permissions
from .models import InventoryMovement
from .serializers import InventoryMovementSerializer
from users.permissions import IsAdmin


class InventoryMovementListCreateView(generics.ListCreateAPIView):
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return InventoryMovement.objects.select_related('product').all()


class InventoryMovementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InventoryMovement.objects.select_related('product').all()
    serializer_class = InventoryMovementSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
