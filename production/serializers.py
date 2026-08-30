from rest_framework import serializers
from .models import ProductionBatch, ProductionTracking, ProcessingRecord


class ProductionBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionBatch
        fields = [
            'id', 'batch_code', 'name', 'description', 'start_date',
            'estimated_processing_date', 'processing_date', 'initial_birds',
            'current_birds', 'mortality', 'initial_average_weight',
            'current_average_weight', 'feed_consumption', 'status',
            'observations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductionTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductionTracking
        fields = [
            'id', 'batch', 'date', 'birds_count', 'average_weight',
            'feed_consumption', 'mortality', 'observations'
        ]
        read_only_fields = ['id']


class ProcessingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingRecord
        fields = [
            'id', 'batch', 'processing_date', 'processed_birds',
            'live_weight_total', 'processed_weight', 'average_weight',
            'waste', 'waste_percentage', 'observations'
        ]
        read_only_fields = ['id']
