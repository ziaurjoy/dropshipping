from django.shortcuts import render

# Create your views here.

import re
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from decimal import Decimal
from cart_app.models import Cart
from users_app.models import DeliveryAddress
from .models import Order, OrderItem, Payment, Shipment, Coupon, ShipmentSetting, ShippingZone, SupportTicket
from .serializers import (CouponSerializer, OrderItemSerializer, OrderSerializer,
    PaymentSerializer, ShipmentSerializer, ShippingMethodSerializer, ShippingZoneSerializer,
    SupportTicketSerializer)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        """POST /api/orders/place_order/ → converts current cart to order"""

        cart = Cart.objects.filter(user=request.user).first()
        print('cart===', cart)
        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

        address_id = request.data.get('address_id')
        shipping_charge = request.data.get('shipping_charge')

        if not address_id or shipping_charge is None:
            return Response({"error": "address_id and shipping_charge are required"},
                          status=status.HTTP_400_BAD_REQUEST)

        address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)

        # try:
        #     with transaction.atomic():   # ← This is the key part
                # Calculate totals
        subtotal = sum(item.total_price for item in cart.items.all())
        total = subtotal + float(shipping_charge)

        # Create Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal=subtotal,
            shipping_charge=float(shipping_charge),
            total=total,
            # coupon=cart.coupon
        )

        # Create OrderItems
        print('cart.items.all()', cart.items.all())
        for cart_item in cart.items.all():
            product = cart_item.product  # assuming this is a dict or JSONField
            variant = cart_item.variant

            product['variant'] = variant  # Add variant details to product snapshot

            # Extract price safely
            price_str = str(variant.get("price", "0") if isinstance(variant, dict) else "0")
            match = re.search(r"([\d.]+)", price_str)
            amount = float(match.group(1)) if match else 0.0

            for key, value in cart_item.quantity.items():
                print(f"===quantity key: {key}, value: {value}")
                OrderItem.objects.create(
                    order=order,
                    product=product,          # Be careful: if product is dict, make sure field accepts it
                    unit_price=amount,
                    quantity=value,
                    # total=amount * cart_item.quantity
                    total=amount * value
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

                # # Clear cart (only if everything above succeeded)
                # cart.items.all().delete()

                # Optionally delete cart itself if it's now empty
                # cart.delete()

        # except Exception as e:
        #     print(f"Error placing order: {str(e)}")  # For debugging, replace with proper logging in production
        #     # Log the error in production
        #     # logger.error(f"Order placement failed: {str(e)}")
        #     return Response({
        #         "message": "Failed to place order. Please try again.",
        #     }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # If we reach here, transaction was successful
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=False, methods=['post'])
    # def place_order(self, request):
    #     """POST /api/orders/place_order/ → converts current cart to order"""
    #     cart = Cart.objects.filter(user=request.user).first()
    #     if not cart or not cart.items.exists():
    #         return Response({"error": "Cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    #     address_id = request.data.get('address_id')
    #     shipping_charge = request.data.get('shipping_charge')
    #     address = get_object_or_404(DeliveryAddress, id=address_id, user=request.user)

    #     # Calculate totals
    #     subtotal = sum(item.total_price for item in cart.items.all())
    #     total = subtotal + float(shipping_charge)

    #     # Create Order
    #     order = Order.objects.create(
    #         user=request.user,
    #         address=address,
    #         subtotal=subtotal,
    #         shipping_charge=shipping_charge,
    #         total=total,
    #         # coupon=cart.coupon
    #     )


    #     # Create OrderItems
    #     for cart_item in cart.items.all():
    #         product = cart_item.product
    #         product["variant"] = cart_item.variant
    #         price_str = cart_item.variant.get("price", "0")

    #         match = re.search(r"([\d.]+)", price_str)
    #         amount = float(match.group(1)) if match else 0

    #         OrderItem.objects.create(
    #             order=order,
    #             # variant=variant,
    #             product=product,
    #             # sku=product.sku,
    #             unit_price=amount,
    #             quantity=cart_item.quantity,
    #             total=amount * cart_item.quantity
    #         )

    #     # Create initial Payment (COD by default)
    #     Payment.objects.create(
    #         order=order,
    #         method='cod',
    #         amount=total,
    #         status='pending'
    #     )

    #     # Create Shipment record
    #     Shipment.objects.create(order=order)

    #     # Clear cart
    #     cart.items.all().delete()

    #     serializer = self.get_serializer(order)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)


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



class ShippingMethodViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ShipmentSetting.objects.all()

    def get_queryset(self):
        return self.queryset.filter(is_active=True).order_by('priority')