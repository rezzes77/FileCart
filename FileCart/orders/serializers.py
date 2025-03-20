from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product


class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "user", "status", "status_display", "total_price", "created_at", "items"]

    def get_total_price(self, obj):
        return f"{obj.total_price} сом"

    def get_status_display(self, obj):
        """Возвращает читаемое название статуса"""
        return dict(Order.STATUS_CHOICES).get(obj.status, obj.status)

class OrderHistorySerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'total_price', 'created_at', 'items']