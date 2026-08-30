from django.urls import path
from .views import NotificationListCreateView, NotificationDetailView, NotificationReadView, mark_all_read

urlpatterns = [
    path('', NotificationListCreateView.as_view(), name='notification-list'),
    path('<int:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:pk>/read/', NotificationReadView.as_view(), name='notification-read'),
    path('mark-all-read/', mark_all_read, name='notification-mark-all-read'),
]
