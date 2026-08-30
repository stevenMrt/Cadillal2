from rest_framework import generics, permissions
from .models import Setting
from .serializers import SettingSerializer
from users.permissions import IsAdmin


class SettingListCreateView(generics.ListCreateAPIView):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]


class SettingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Setting.objects.all()
    serializer_class = SettingSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
