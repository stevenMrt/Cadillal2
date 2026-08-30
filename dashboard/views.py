from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdmin
from django.db.models import Count, Sum, F
from orders.models import Order
from sales.models import Sale
from customers.models import Customer
from products.models import Product
from users.models import User


class DashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        total_orders = Order.objects.count()
        total_sales = Sale.objects.count()
        total_customers = Customer.objects.count()
        total_products = Product.objects.count()
        total_users = User.objects.count()
        low_stock_products = Product.objects.filter(stock__lt=F('min_stock')).count()
        pending_orders = Order.objects.filter(status='pending').count()
        recent_orders = Order.objects.order_by('-created_at')[:5]

        recent_orders_data = [
            {
                'id': order.id,
                'customer': order.customer.full_name if order.customer else '',
                'total': str(order.total),
                'status': order.status,
                'created_at': order.created_at.isoformat(),
            }
            for order in recent_orders
        ]

        return Response({
            'total_orders': total_orders,
            'total_sales': total_sales,
            'total_customers': total_customers,
            'total_products': total_products,
            'total_users': total_users,
            'low_stock_products': low_stock_products,
            'pending_orders': pending_orders,
            'recent_orders': recent_orders_data,
        })
