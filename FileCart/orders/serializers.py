from rest_framework import serializers
from .models import Cart, CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source="product"
    )

    class Meta:
        model = CartItem
        fields = ["id", "product", "product_id", "quantity", "added_at"]


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "user", "items"]

from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source="product")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_id", "quantity", "price"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "user", "status", "total_price", "created_at", "items"]