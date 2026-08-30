from django.urls import path
from .views import InventoryMovementListCreateView, InventoryMovementDetailView

urlpatterns = [
    path('', InventoryMovementListCreateView.as_view(), name='inventory-movement-list'),
    path('<int:pk>/', InventoryMovementDetailView.as_view(), name='inventory-movement-detail'),
]
