from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CartItemViewSet, CartView, OrderViewSet, ProductViewSet, RegisterView
from .views_profile import ProfileView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('cart/items', CartItemViewSet, basename='cart-item')
router.register('orders', OrderViewSet, basename='order')
router.register('register', RegisterView, basename='register')

urlpatterns = [
    path('', include(router.urls)),
    path('cart/', CartView.as_view(), name='cart'),
    path('auth/me/', ProfileView.as_view(), name='me'),
]
