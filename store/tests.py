from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cart, CartItem, Order, Product

User = get_user_model()


class EcommerceAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='buyer', password='password123', email='buyer@example.com'
        )
        self.admin = User.objects.create_superuser(
            username='admin', password='password123', email='admin@example.com'
        )
        self.product = Product.objects.create(
            name='Test Product', price=Decimal('9.99'), stock=10
        )

    def authenticate(self, user=None):
        user = user or self.user
        self.client.force_authenticate(user=user)

    def test_register(self):
        url = reverse('register-list')
        payload = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'strongpass123',
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_product_list_public(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_add_item_to_cart(self):
        self.authenticate()
        url = reverse('cart-item-list')
        payload = {'product_id': self.product.id, 'quantity': 2}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 1)
        self.assertEqual(cart.items.first().quantity, 2)

    def test_checkout_creates_order_and_clears_cart(self):
        self.authenticate()
        Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=self.user.cart, product=self.product, quantity=1)

        url = reverse('order-list')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertEqual(self.user.cart.items.count(), 0)

    def test_pay_order(self):
        self.authenticate()
        Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=self.user.cart, product=self.product, quantity=1)
        order_resp = self.client.post(reverse('order-list'), {}, format='json')
        order_id = order_resp.data['id']

        pay_url = reverse('order-pay', args=[order_id])
        resp = self.client.post(pay_url, {}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.STATUS_PAID)

    def test_preparation_flow(self):
        # user creates order
        self.authenticate(self.user)
        Cart.objects.get_or_create(user=self.user)
        CartItem.objects.create(cart=self.user.cart, product=self.product, quantity=2)
        order_resp = self.client.post(reverse('order-list'), {}, format='json')
        order_id = order_resp.data['id']

        # staff pays then prepares
        self.client.force_authenticate(user=self.admin)
        self.client.post(reverse('order-pay', args=[order_id]), {}, format='json')
        prepare_url = reverse('order-prepare', args=[order_id])
        resp = self.client.post(
            prepare_url,
            {
                'items': [
                    {
                        'id': Order.objects.get(id=order_id).items.first().id,
                        'prepared_quantity': 2,
                    }
                ]
            },
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.STATUS_PREPARED)
