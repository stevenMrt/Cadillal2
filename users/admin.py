from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)
    fields = ('email', 'username', 'first_name', 'last_name', 'role', 'phone', 'document', 'birth_date', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
    readonly_fields = ('date_joined',)
