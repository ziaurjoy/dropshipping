

from rest_framework import serializers
from products_app.models import Product
from .models import CartItem, Cart

# If you don't have ProductMinimalSerializer yet, add this simple one:
class ProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]  # add image, etc. if you want


class CartItemSerializer(serializers.ModelSerializer):
    # product = ProductMinimalSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", 'variant',  "total_price", "added_at"]

    def get_total_price(self, obj):

        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price", "created_at", "updated_at"]

    def get_total_price(self, obj):
        return obj.total_price