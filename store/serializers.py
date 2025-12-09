from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem, Product

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'stock',
            'image_url',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        source='product',
        queryset=Product.objects.filter(is_active=True),
        write_only=True,
    )
    subtotal = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = (
            'id',
            'product',
            'product_id',
            'quantity',
            'subtotal',
            'added_at',
        )
        read_only_fields = ('id', 'product', 'subtotal', 'added_at')

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return value

    def validate(self, attrs):
        product = attrs.get('product') or getattr(self.instance, 'product', None)
        quantity = attrs.get('quantity', getattr(self.instance, 'quantity', 1))
        if product and product.stock < quantity:
            raise serializers.ValidationError('Insufficient stock for this product.')
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ('id', 'items', 'total', 'updated_at')
        read_only_fields = ('id', 'items', 'total', 'updated_at')

    def get_total(self, obj):
        total = sum((item.subtotal for item in obj.items.all()), Decimal('0'))
        return total.quantize(Decimal('0.01'))


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    subtotal = serializers.SerializerMethodField()
    prepared_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product',
            'quantity',
            'prepared_quantity',
            'unit_price',
            'subtotal',
        )
        read_only_fields = ('id', 'product', 'unit_price', 'subtotal', 'prepared_quantity')

    def get_subtotal(self, obj):
        return obj.subtotal.quantize(Decimal('0.01'))


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'user',
            'status',
            'total_amount',
            'placed_at',
            'updated_at',
            'items',
        )
        read_only_fields = ('id', 'total_amount', 'placed_at', 'updated_at', 'items')

    def get_user(self, obj):
        return {'id': obj.user_id, 'username': getattr(obj.user, 'username', None)}


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)


class PreparationItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    prepared_quantity = serializers.IntegerField(min_value=0)
