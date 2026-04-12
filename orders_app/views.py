from django.shortcuts import render

# Create your views here.


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from cart_app.models import Cart
from users_app.models import DeliveryAddress
from .models import Order, OrderItem, Payment, Shipment, Coupon, ShippingZone, SupportTicket
from .serializers import (
    OrderSerializer, OrderItemSerializer,
    PaymentSerializer, ShippingZoneSerializer, ShipmentSerializer,
    SupportTicketSerializer, CouponSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        """POST /api/orders/place_order/ → converts current cart to order"""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('address_id')
        shipping_charge = request.data.get('shipping_charge')
        print("Received address_id:", address_id)  # Debugging line
        address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)

        # Calculate totals
        subtotal = sum(item.total_price for item in cart.items.all())
        total = subtotal + Decimal(str(shipping_charge))

        for item in cart.items.all():
            print(f"CartItem: {item.product_id}, Quantity: {item.quantity}, Total Price: {item.total_price}")

        return Response({"subtotal": subtotal, "total": total}, status=status.HTTP_200_OK)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal=subtotal,
            shipping_charge=shipping_charge,
            total=total,
            # coupon=cart.coupon
        )

        # Create OrderItems
        for cart_item in cart.items.all():
            product = cart_item.product
            OrderItem.objects.create(
                order=order,
                # variant=variant,
                product_name=product.name,
                # sku=product.sku,
                unit_price=product.price,
                quantity=cart_item.quantity,
                line_total=product.price * cart_item.quantity
            )

        # Create initial Payment (COD by default)
        Payment.objects.create(
            order=order,
            method='cod',
            amount=total,
            status='pending'
        )

        # Create Shipment record
        Shipment.objects.create(order=order)

        # Clear cart
        # cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class AddressViewSet(viewsets.ModelViewSet):
#     serializer_class = AddressSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Address.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# Other simple read/write ViewSets
class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


# class ShippingZoneViewSet(viewsets.ReadOnlyModelViewSet):
class ShippingZoneViewSet(viewsets.ModelViewSet):
    queryset = ShippingZone.objects.all()
    serializer_class = ShippingZoneSerializer
    permission_classes = [permissions.IsAuthenticated]


# class ShipmentViewSet(viewsets.ModelViewSet):
#     serializer_class = ShipmentSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Shipment.objects.filter(order__user=self.request.user)


class ShipmentViewSet(viewsets.ModelViewSet):
    queryset = Shipment.objects.all()
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        carrier = request.data.get('carrier')

        if not order_id:
            return Response({"error": "order_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not carrier:
            return Response({"error": "carrier is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if order exists
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if shipment already exists for this order
        if hasattr(order, 'shipment'):
            return Response({"error": "Shipment already exists for this order"},
                          status=status.HTTP_400_BAD_REQUEST)

        # Create shipment - only order and carrier from user, rest auto-generated
        shipment = Shipment.objects.create(
            order=order,
            carrier=carrier.strip()
        )

        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SupportTicket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)