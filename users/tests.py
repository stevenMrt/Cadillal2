from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from categories.models import Category
from products.models import Product
from customers.models import Customer
from orders.models import Order, OrderItem
from payments.models import Payment
from inventory.models import InventoryMovement
from notifications.models import Notification
from django.test import TestCase


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_register(self):
        url = reverse('register')
        data = {
            'email': 'new@test.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='new@test.com').exists())

    def test_login(self):
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'adminpass'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {'email': 'admin@test.com', 'password': 'wrong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_authenticated(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'customer@test.com')

    def test_profile_unauthenticated(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_cannot_access_admin_users(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('admin-user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_category(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.post(url, {'name': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_create_product(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        response = self.client.post(url, {'name': 'Test', 'price': 10, 'stock': 5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_access_settings(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('setting-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_access_inventory(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('inventory-movement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_access_sales(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('sale-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_access_production(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('batch-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_admin_users(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('admin-user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class OwnershipTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer_a = User.objects.create_user(
            username='customer_a@test.com', email='customer_a@test.com', password='customerpass', role='customer'
        )
        self.customer_b = User.objects.create_user(
            username='customer_b@test.com', email='customer_b@test.com', password='customerpass', role='customer'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product', price=10, cost=5, stock=100, category=self.category
        )
        self.order_a = Order.objects.create(
            customer=self.customer_a, subtotal=10, tax=0, total=10
        )
        OrderItem.objects.create(order=self.order_a, product_name='Test', quantity=1, unit_price=10, subtotal=10)
        self.payment_a = Payment.objects.create(
            order=self.order_a, method='cash', amount=10, status='paid'
        )
        self.address_a = self.customer_a.addresses.create(
            label='Home', street='123 Main St', city='Bogota', state='Cundinamarca', zip_code='111111'
        )
        self.notification_a = Notification.objects.create(
            user=self.customer_a, title='Test', message='Test message'
        )

    def test_customer_a_cannot_view_order_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('order-detail', args=[self.order_a.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        url_b = reverse('order-detail', args=[9999])
        response = self.client.get(url_b)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_a_cannot_modify_order_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_a)
        order_b = Order.objects.create(customer=self.customer_b, subtotal=10, tax=0, total=10)
        url = reverse('order-detail', args=[order_b.id])
        response = self.client.patch(url, {'notes': 'hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_a_cannot_view_payment_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-detail', args=[self.payment_a.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order_b = Order.objects.create(customer=self.customer_b, subtotal=10, tax=0, total=10)
        payment_b = Payment.objects.create(order=order_b, method='cash', amount=10)
        url = reverse('payment-detail', args=[payment_b.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_a_cannot_modify_payment_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_a)
        order_b = Order.objects.create(customer=self.customer_b, subtotal=10, tax=0, total=10)
        payment_b = Payment.objects.create(order=order_b, method='cash', amount=10)
        url = reverse('payment-detail', args=[payment_b.id])
        response = self.client.patch(url, {'amount': 999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_a_cannot_view_address_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('address-detail', args=[self.address_a.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_a_cannot_modify_address_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('address-detail', args=[self.address_a.id])
        response = self.client.patch(url, {'street': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_a_cannot_access_notification_of_customer_b(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('notification-detail', args=[self.notification_a.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product', price=10, cost=5, stock=100, category=self.category
        )

    def test_create_order(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        data = {
            'items': [{'product_id': self.product.id, 'product_name': 'Test Product', 'quantity': 1, 'unit_price': 10, 'subtotal': 10}],
            'subtotal': 10,
            'tax': 0,
            'total': 10,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 99)

    def test_create_order_insufficient_stock(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        data = {
            'items': [{'product_id': self.product.id, 'product_name': 'Test Product', 'quantity': 200, 'unit_price': 10, 'subtotal': 2000}],
            'subtotal': 2000,
            'tax': 0,
            'total': 2000,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 100)

    def test_stock_never_negative(self):
        self.product.stock = 5
        self.product.save()
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        data = {
            'items': [{'product_id': self.product.id, 'product_name': 'Test Product', 'quantity': 3, 'unit_price': 10, 'subtotal': 30}],
            'subtotal': 30,
            'tax': 0,
            'total': 30,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

    def test_cancel_order_restores_stock(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        data = {
            'items': [{'product_id': self.product.id, 'product_name': 'Test Product', 'quantity': 5, 'unit_price': 10, 'subtotal': 50}],
            'subtotal': 50,
            'tax': 0,
            'total': 50,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 95)

        url_detail = reverse('order-detail', args=[order_id])
        response = self.client.patch(url_detail, {'status': 'cancelled'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 100)

    def test_no_double_discount_on_update(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('order-list')
        data = {
            'items': [{'product_id': self.product.id, 'product_name': 'Test Product', 'quantity': 2, 'unit_price': 10, 'subtotal': 20}],
            'subtotal': 20,
            'tax': 0,
            'total': 20,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        order_id = response.data['id']
        self.product.refresh_from_db()
        stock_after_create = self.product.stock

        url_detail = reverse('order-detail', args=[order_id])
        data_update = {
            'items': [{'product_id': self.product.id, 'product_name': 'Test Product', 'quantity': 1, 'unit_price': 10, 'subtotal': 10}],
            'subtotal': 10,
            'tax': 0,
            'total': 10,
        }
        response = self.client.patch(url_detail, data_update, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, stock_after_create + 1)


class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer_a = User.objects.create_user(
            username='customer_a@test.com', email='customer_a@test.com', password='customerpass', role='customer'
        )
        self.customer_b = User.objects.create_user(
            username='customer_b@test.com', email='customer_b@test.com', password='customerpass', role='customer'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product', price=10, cost=5, stock=100, category=self.category
        )
        self.order_a = Order.objects.create(
            customer=self.customer_a, subtotal=10, tax=0, total=10
        )
        self.order_b = Order.objects.create(
            customer=self.customer_b, subtotal=20, tax=0, total=20
        )

    def test_create_payment_for_own_order(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        data = {'order': self.order_a.id, 'method': 'cash', 'amount': 10, 'status': 'paid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 1)
        self.assertEqual(Payment.objects.first().order, self.order_a)

    def test_customer_cannot_create_payment_for_other_order(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        data = {'order': self.order_b.id, 'method': 'cash', 'amount': 10, 'status': 'paid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_amount_exceeds_order_total(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        data = {'order': self.order_a.id, 'method': 'cash', 'amount': 999, 'status': 'paid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_status_transition_valid(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        data = {'order': self.order_a.id, 'method': 'cash', 'amount': 10, 'status': 'pending'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_id = response.data['id']
        url_detail = reverse('payment-detail', args=[payment_id])
        response = self.client.patch(url_detail, {'status': 'paid'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_payment_status_transition_invalid(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        data = {'order': self.order_a.id, 'method': 'cash', 'amount': 10, 'status': 'paid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment_id = response.data['id']
        url_detail = reverse('payment-detail', args=[payment_id])
        response = self.client.patch(url_detail, {'status': 'pending'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_duplicate_payments(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        data = {'order': self.order_a.id, 'method': 'cash', 'amount': 6, 'status': 'paid'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_receipt_upload(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('payment-list')
        receipt_file = SimpleUploadedFile('receipt.jpg', b'fake image content', content_type='image/jpeg')
        data = {
            'order': self.order_a.id,
            'method': 'bank',
            'amount': 10,
            'status': 'paid',
            'receipt': receipt_file,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('receipt_url', response.data)


class InventoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product', price=10, cost=5, stock=100, category=self.category
        )

    def test_inventory_movement_consistency(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('inventory-movement-list')
        data = {
            'product': self.product.id,
            'movement_type': 'out',
            'quantity': 5,
            'previous_stock': 100,
            'new_stock': 95,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InventoryMovement.objects.count(), 1)

    def test_inventory_movement_inconsistent_stock(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('inventory-movement-list')
        data = {
            'product': self.product.id,
            'movement_type': 'out',
            'quantity': 5,
            'previous_stock': 100,
            'new_stock': 999,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_inventory_movement_negative_stock(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('inventory-movement-list')
        data = {
            'product': self.product.id,
            'movement_type': 'out',
            'quantity': 200,
            'previous_stock': 100,
            'new_stock': -100,
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CategoryAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_can_get_categories(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_post_category(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('category-list')
        response = self.client.post(url, {'name': 'Test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_put_category(self):
        self.client.force_authenticate(user=self.customer)
        category = Category.objects.create(name='Test')
        url = reverse('category-detail', args=[category.id])
        response = self.client.put(url, {'name': 'Test2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_customer_cannot_delete_category(self):
        self.client.force_authenticate(user=self.customer)
        category = Category.objects.create(name='Test')
        url = reverse('category-detail', args=[category.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_category(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('category-list')
        response = self.client.post(url, {'name': 'Admin Category'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        category_id = response.data['id']
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(reverse('category-detail', args=[category_id]), {'name': 'Updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(reverse('category-detail', args=[category_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ProductAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )
        self.category = Category.objects.create(name='Test Category')

    def test_customer_can_get_products(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_customer_cannot_post_product(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('product-list')
        response = self.client.post(url, {'name': 'Test', 'price': 10, 'stock': 5, 'category': self.category.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_product(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('product-list')
        response = self.client.post(url, {'name': 'Admin Product', 'description': 'Test', 'sku': 'SKU-001', 'price': 10, 'cost': 5, 'stock': 5, 'category_id': self.category.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        product_id = response.data['id']
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(reverse('product-detail', args=[product_id]), {'name': 'Updated', 'description': 'Test', 'sku': 'SKU-001', 'price': 10, 'cost': 5, 'stock': 5, 'category_id': self.category.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(reverse('product-detail', args=[product_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CustomerAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_cannot_list_customers(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_customers(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('customer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class SettingsAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_cannot_access_settings(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('setting-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_settings(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('setting-list')
        response = self.client.post(url, {'key': 'test', 'value': 'value'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        setting_id = response.data['id']
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(reverse('setting-detail', args=[setting_id]), {'key': 'test', 'value': 'updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(reverse('setting-detail', args=[setting_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class InventoryAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product', price=10, cost=5, stock=100, category=self.category
        )

    def test_customer_cannot_access_inventory(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('inventory-movement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_inventory(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('inventory-movement-list')
        response = self.client.post(url, {'product': self.product.id, 'movement_type': 'in', 'quantity': 10, 'previous_stock': 100, 'new_stock': 110}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        movement_id = response.data['id']
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.put(reverse('inventory-movement-detail', args=[movement_id]), {'product': self.product.id, 'movement_type': 'out', 'quantity': 5, 'previous_stock': 110, 'new_stock': 105}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(reverse('inventory-movement-detail', args=[movement_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class SalesAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_cannot_access_sales(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('sale-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_sales(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('sale-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ProductionAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_cannot_access_production(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('batch-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_crud_production(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('batch-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class DashboardAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer = User.objects.create_user(
            username='customer@test.com', email='customer@test.com', password='customerpass', role='customer'
        )

    def test_customer_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.customer)
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_dashboard(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_orders', response.data)


class NotificationAdminTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin@test.com', email='admin@test.com', password='adminpass', role='admin'
        )
        self.customer_a = User.objects.create_user(
            username='customer_a@test.com', email='customer_a@test.com', password='customerpass', role='customer'
        )
        self.customer_b = User.objects.create_user(
            username='customer_b@test.com', email='customer_b@test.com', password='customerpass', role='customer'
        )
        self.notification_a = Notification.objects.create(
            user=self.customer_a, title='Test A', message='Test message A'
        )
        self.notification_b = Notification.objects.create(
            user=self.customer_b, title='Test B', message='Test message B'
        )

    def test_customer_sees_own_notifications(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], self.notification_a.id)

    def test_customer_cannot_modify_other_notification(self):
        self.client.force_authenticate(user=self.customer_a)
        url = reverse('notification-detail', args=[self.notification_b.id])
        response = self.client.patch(url, {'is_read': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_access_all_notifications(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('notification-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class AddressOwnershipTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_a = User.objects.create_user(
            username='customer_a@test.com', email='customer_a@test.com', password='customerpass', role='customer'
        )
        self.customer_b = User.objects.create_user(
            username='customer_b@test.com', email='customer_b@test.com', password='customerpass', role='customer'
        )
        self.address_a = self.customer_a.addresses.create(
            label='Home', street='123 Main St', city='Bogota', state='Cundinamarca', zip_code='111111'
        )

    def test_customer_b_cannot_view_address_a(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('address-detail', args=[self.address_a.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_b_cannot_modify_address_a(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('address-detail', args=[self.address_a.id])
        response = self.client.patch(url, {'street': 'Hacked'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_b_cannot_delete_address_a(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('address-detail', args=[self.address_a.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PaymentMethodOwnershipTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer_a = User.objects.create_user(
            username='customer_a@test.com', email='customer_a@test.com', password='customerpass', role='customer'
        )
        self.customer_b = User.objects.create_user(
            username='customer_b@test.com', email='customer_b@test.com', password='customerpass', role='customer'
        )
        self.method_a = self.customer_a.payment_methods.create(
            type='bank', last_four='1234', expiry_date='12/2025', holder_name='Customer A'
        )

    def test_customer_b_cannot_view_method_a(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('payment-method-detail', args=[self.method_a.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_b_cannot_modify_method_a(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('payment-method-detail', args=[self.method_a.id])
        response = self.client.patch(url, {'last_four': '9999'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_customer_b_cannot_delete_method_a(self):
        self.client.force_authenticate(user=self.customer_b)
        url = reverse('payment-method-detail', args=[self.method_a.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='reset@test.com', email='reset@test.com', password='oldpass123', role='customer'
        )

    def test_password_reset_request_for_existing_email(self):
        url = reverse('password-reset-request')
        response = self.client.post(url, {'email': self.user.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)

    def test_password_reset_request_for_nonexistent_email(self):
        url = reverse('password-reset-request')
        response = self.client.post(url, {'email': 'nonexistent@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)

    def test_password_reset_confirm_changes_password(self):
        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        from django.utils import timezone

        self.user.last_login = timezone.now()
        self.user.save(update_fields=['last_login'])

        token_generator = PasswordResetTokenGenerator()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = token_generator.make_token(self.user)

        url = reverse('password-reset-confirm')
        response = self.client.post(url, {
            'uid': uid,
            'token': token,
            'new_password': 'newpass456',
        }, format='json')
        print('PASSWORD RESET RESPONSE:', response.status_code, response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass456'))

    def test_password_reset_confirm_with_invalid_token(self):
        url = reverse('password-reset-confirm')
        response = self.client.post(url, {
            'uid': self.user.pk,
            'token': 'invalid-token',
            'new_password': 'newpass456',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
