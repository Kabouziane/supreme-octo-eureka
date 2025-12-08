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
