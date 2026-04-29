from rest_framework import serializers
from products_app.models import ProductImage
from .models import (
     Coupon, Order, OrderItem, Payment, ShipmentSetting,
    ShippingZone, Shipment, SupportTicket
)
from products_app.serializers import ProductVariantSerializer
from users_app.serializers import DeliveryAddressSerializer

# class AddressSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Address
#         fields = '__all__'


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity', 'total']

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print('=========', ProductImage.objects.filter(product=instance.product, is_primary=True))
    #     image = ProductImage.objects.filter(product=instance.product, is_primary=True).first()
    #     representation['image_url'] = image.url if image else None

    #     return representation


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = DeliveryAddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'address', 'status',
            'subtotal', 'discount_amount', 'shipping_charge', 'total',
            'coupon', 'notes', 'created_at', 'items'
        ]
        read_only_fields = ['order_number', 'subtotal', 'total', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class ShippingZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingZone
        fields = '__all__'


# class ShipmentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Shipment
#         fields = '__all__'


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'carrier', 'tracking_number','tracking_url', 'estimated_delivery', 'status', 'shipped_at'
            ]
        read_only_fields = ['id', 'tracking_number', 'tracking_url', 'estimated_delivery', 'shipped_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = '__all__'

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentSetting
        fields = '__all__'