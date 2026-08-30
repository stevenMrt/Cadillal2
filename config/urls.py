from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('users.urls')),
    path('api/roles/', include('roles.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/products/', include('products.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/addresses/', include('addresses.urls')),
    path('api/payment-methods/', include('payment_methods.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/production/', include('production.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
