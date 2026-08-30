from django.db import models


class ProductionBatch(models.Model):
    STATUS_CHOICES = (
        ('planned', 'Planificado'),
        ('in_breeding', 'En crianza'),
        ('ready_for_processing', 'Listo para procesamiento'),
        ('processed', 'Procesado'),
        ('finished', 'Finalizado'),
        ('cancelled', 'Cancelado'),
    )

    batch_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    estimated_processing_date = models.DateField(blank=True, null=True)
    processing_date = models.DateField(blank=True, null=True)
    initial_birds = models.IntegerField()
    current_birds = models.IntegerField()
    mortality = models.IntegerField(default=0)
    initial_average_weight = models.FloatField()
    current_average_weight = models.FloatField()
    feed_consumption = models.FloatField(default=0)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='planned')
    observations = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.batch_code


class ProductionTracking(models.Model):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE, related_name='trackings')
    date = models.DateField()
    birds_count = models.IntegerField()
    average_weight = models.FloatField()
    feed_consumption = models.FloatField()
    mortality = models.IntegerField(default=0)
    observations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.batch.batch_code} - {self.date}'


class ProcessingRecord(models.Model):
    batch = models.ForeignKey(ProductionBatch, on_delete=models.CASCADE, related_name='processings')
    processing_date = models.DateField()
    processed_birds = models.IntegerField()
    live_weight_total = models.FloatField()
    processed_weight = models.FloatField()
    average_weight = models.FloatField()
    waste = models.FloatField()
    waste_percentage = models.FloatField()
    observations = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.batch.batch_code} - {self.processing_date}'
