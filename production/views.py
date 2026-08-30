from rest_framework import generics, permissions
from .models import ProductionBatch, ProductionTracking, ProcessingRecord
from .serializers import (
    ProductionBatchSerializer,
    ProductionTrackingSerializer,
    ProcessingRecordSerializer,
)
from users.permissions import IsAdmin


class ProductionBatchListCreateView(generics.ListCreateAPIView):
    queryset = ProductionBatch.objects.all()
    serializer_class = ProductionBatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class ProductionBatchDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductionBatch.objects.all()
    serializer_class = ProductionBatchSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class ProductionTrackingListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductionTrackingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return ProductionTracking.objects.filter(batch_id=self.kwargs['batch_id'])


class ProcessingRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = ProcessingRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return ProcessingRecord.objects.filter(batch_id=self.kwargs['batch_id'])

    def perform_create(self, serializer):
        serializer.save(batch_id=self.kwargs['batch_id'])


class ProcessingRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProcessingRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get_queryset(self):
        return ProcessingRecord.objects.filter(batch_id=self.kwargs['batch_id'])
