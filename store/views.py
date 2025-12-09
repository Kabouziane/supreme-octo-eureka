from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Order, OrderItem, Product
from .serializers import (
    CartItemSerializer,
    CartSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    PreparationItemSerializer,
    ProductSerializer,
    RegisterSerializer,
)

User = get_user_model()


class RegisterView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class CartItemViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related('product')

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

    def perform_update(self, serializer):
        serializer.save()


class OrderViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related('user').prefetch_related('items__product')
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('items__product')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.select_related('product')
        if not items.exists():
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user)
        for cart_item in items:
            product = cart_item.product
            if cart_item.quantity > product.stock:
                transaction.set_rollback(True)
                return Response(
                    {'detail': f'Insufficient stock for {product.name}.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            product.stock -= cart_item.quantity
            product.save(update_fields=['stock'])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                unit_price=product.price,
            )
        order.recalculate_total()
        items.delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        order = self.get_object()
        if order.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Not allowed.'}, status=status.HTTP_403_FORBIDDEN)
        if order.status != Order.STATUS_PENDING:
            return Response({'detail': 'Order not pending.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.STATUS_PAID
        order.save(update_fields=['status', 'updated_at'])
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def set_status(self, request, pk=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def prepare(self, request, pk=None):
        order = self.get_object()
        if order.status not in [Order.STATUS_PAID, Order.STATUS_PREPARED]:
            return Response(
                {'detail': 'Order must be paid before preparation.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        items_data = request.data.get('items', [])
        serializer = PreparationItemSerializer(data=items_data, many=True)
        serializer.is_valid(raise_exception=True)

        items_map = {item.id: item for item in order.items.all()}
        for item_data in serializer.validated_data:
            item_id = item_data['id']
            prepared_qty = item_data['prepared_quantity']
            item = items_map.get(item_id)
            if not item:
                continue
            item.prepared_quantity = min(prepared_qty, item.quantity)
            item.save(update_fields=['prepared_quantity'])

        order.update_preparation_status()
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def ready_to_ship(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.STATUS_PREPARED:
            return Response({'detail': 'Order must be prepared first.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.STATUS_READY_TO_SHIP
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def ship(self, request, pk=None):
        order = self.get_object()
        if order.status not in [Order.STATUS_READY_TO_SHIP, Order.STATUS_PREPARED, Order.STATUS_PAID]:
            return Response({'detail': 'Order not ready to ship.'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = Order.STATUS_SHIPPED
        order.save(update_fields=['status', 'updated_at'])
        return Response(OrderSerializer(order).data)
