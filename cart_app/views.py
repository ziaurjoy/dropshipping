
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products_app.models import Product


class CartView(APIView):

    permission_classes = [IsAuthenticated]

    def get_or_create_cart(self, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    # GET /api/cart/ → View full cart
    def get(self, request):
        cart = self.get_or_create_cart(request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart = self.get_or_create_cart(request.user)
        items_data = request.data

        # Support single item or list
        if isinstance(items_data, dict):
            items_data = [items_data]

        results = []
        for item_data in items_data:
            product_id = item_data.get("product_id")
            quantity = int(item_data.get("quantity", 1))

            if not product_id or quantity < 1:
                continue

            product = get_object_or_404(Product, id=product_id)

            # Add or increase quantity
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={"quantity": quantity}
            )
            if not created:
                cart_item.quantity = quantity          # merge quantities
                cart_item.save()

            results.append(cart_item)

        serializer = CartItemSerializer(results, many=True)
        return Response({
            "message": "Items added to cart successfully",
            "added_items": serializer.data,
            "cart_total": cart.total_price
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        cart = self.get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

