from django.urls import path
from .views import SettingListCreateView, SettingDetailView

urlpatterns = [
    path('', SettingListCreateView.as_view(), name='setting-list'),
    path('<int:pk>/', SettingDetailView.as_view(), name='setting-detail'),
]
