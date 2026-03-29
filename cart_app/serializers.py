from rest_framework import serializers
from .models import Cart, CartItem
from products_app.serializers import ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'quantity', 'line_total']

    def get_line_total(self, obj):
        return obj.line_total


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_key', 'coupon',
            'items', 'subtotal', 'total', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_subtotal(self, obj):
        return sum(item.line_total for item in obj.items.all())

    def get_total(self, obj):
        subtotal = self.get_subtotal(obj)
        # Coupon discount will be calculated in view later
        return subtotal