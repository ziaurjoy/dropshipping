from rest_framework import serializers
from products_app.models import ProductImage
from .models import (
     Coupon, Payment, ShipmentSetting,
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


# class OrderItemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OrderItem
#         fields = ['id', 'product', 'unit_price', 'quantity', 'total']

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     print('=========', ProductImage.objects.filter(product=instance.product, is_primary=True))
    #     image = ProductImage.objects.filter(product=instance.product, is_primary=True).first()
    #     representation['image_url'] = image.url if image else None

    #     return representation


# class OrderSerializer(serializers.ModelSerializer):
#     # items = OrderItemSerializer(many=True, read_only=True)
#     address = DeliveryAddressSerializer(read_only=True)

#     class Meta:
#         model = Order
#         fields = [
#             'id', 'order_number', 'user', 'address', 'status',
#             'subtotal', 'discount_amount', 'shipping_charge', 'total',
#             'coupon', 'notes', 'created_at', 'items'
#         ]
#         read_only_fields = ['order_number', 'subtotal', 'total', 'created_at']


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
    order_number = serializers.SerializerMethodField(read_only=True)
    address = DeliveryAddressSerializer(source='order.address', read_only=True)

    def get_order_number(self, obj):
        return getattr(obj.order, 'order_number', None)
    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'order_number', 'carrier', 'tracking_number','tracking_url', 'estimated_delivery', 'status', 'shipped_at', 'address'
            ]
        read_only_fields = ['id', 'tracking_number', 'tracking_url', 'estimated_delivery', 'shipped_at', 'address']
        # depth = 1



class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = '__all__'

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentSetting
        fields = '__all__'




from rest_framework import serializers
from .models import Order
from cart_app.models import Cart
from users_app.models import DeliveryAddress


class PlaceOrderSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()

    def validate_address_id(self, value):
        user = self.context['request'].user
        # make sure address belongs to this user
        if not DeliveryAddress.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Address not found.")
        return value

    def validate(self, attrs):
        user = self.context['request'].user
        # make sure user has cart items
        if not Cart.objects.filter(user=user).exists():
            raise serializers.ValidationError("Your cart is empty.")
        return attrs

    def create(self, validated_data):
        user       = self.context['request'].user
        address    = DeliveryAddress.objects.get(id=validated_data['address_id'])
        cart_items = Cart.objects.filter(user=user)

        orders = []
        for cart in cart_items:
            # compute total from variants JSONField
            total = 0
            for entry in cart.variants:
                quantity_map = entry.get('quantity', {})
                sizes        = entry.get('variant', {}).get('sizes', [])
                for size in sizes:
                    qty   = quantity_map.get(size['size_name'], 0)
                    price = float(size.get('price', 0))
                    total += qty * price

            order = Order.objects.create(
                user            = user,
                address         = address,
                product_id      = cart.product_id,
                product_name    = cart.product_name,
                product_image   = cart.product_image,
                variants        = cart.variants,       # copy JSON as-is
                shipping_method = cart.shipping_method,
                total_price     = round(total, 2),
            )
            orders.append(order)

        # ── remove cart after order placed ──────────────────
        cart_items.delete()

        return orders


class OrderResponseSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id',
            'order_number',
            'product_id',
            'product_name',
            'product_image',
            'variants',
            'shipping_method',
            'status',
            'status_display',
            'total_price',
            'created_at',
            'updated_at',
        ]


class OrderDetailsResponseSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    address = DeliveryAddressSerializer(read_only=True)
    class Meta:
        model  = Order
        fields = [
            'id',
            'order_number',
            'product_id',
            'product_name',
            'product_image',
            'address',
            'variants',
            'shipping_method',
            'status',
            'status_display',
            'total_price',
            'created_at',
            'updated_at',
        ]