from django.urls import path
from .views import (
    ProductionBatchListCreateView,
    ProductionBatchDetailView,
    ProductionTrackingListCreateView,
    ProcessingRecordListCreateView,
    ProcessingRecordDetailView,
)

urlpatterns = [
    path('batches/', ProductionBatchListCreateView.as_view(), name='batch-list'),
    path('batches/<int:pk>/', ProductionBatchDetailView.as_view(), name='batch-detail'),
    path('batches/<int:batch_id>/trackings/', ProductionTrackingListCreateView.as_view(), name='tracking-list'),
    path('batches/<int:batch_id>/processings/', ProcessingRecordListCreateView.as_view(), name='processing-create'),
    path('batches/<int:batch_id>/processings/<int:pk>/', ProcessingRecordDetailView.as_view(), name='processing-detail'),
]
