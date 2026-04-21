
from requests import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from products_app.services import get_products_details_from_fastapi
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from products_app.models import Product


def match_variant_sizes_with_quantity(variant, quantity):
    sizes = variant.get("sizes", [])

    result = []
    for size in sizes:
        size_name = size.get("size_name")

        if size_name in quantity and quantity[size_name] > 0:
            result.append({
                "size_name": size_name,
                "price": size.get("price"),
                "stock": size.get("stock"),
                "quantity": quantity[size_name]
            })
    return result


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
        _cart = self.get_or_create_cart(request.user)
        items_data = request.data

        if isinstance(items_data, dict):
            items_data = [items_data]

        results = []

        for item_data in items_data:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity", 1)
            variant = item_data.get("variant", "")
            print('Received variant:', variant)
            if not product_id or not quantity:
                continue

            import copy
            product = copy.deepcopy(get_products_details_from_fastapi(product_id=product_id, request=request))

            _product = product.get("product", {})
            details = _product.get("details", {})
            cart_data = details.get("extract_product_title_and_cart", {}).get("cart", {})
            skus = cart_data.get("skus", [])
            variant = match_variant_sizes_with_quantity(variant, quantity)
            # variant = next((s for s in skus if s == variant.get('size')), {})
            print('Found variant:', variant)
            # Remove heavy data
            product["product"].pop("details", None)
            cart_item, created = CartItem.objects.update_or_create(
                cart=_cart,
                product_id=_product.get("_id"),
                # variant_key=_product.get("size_name", ""),
                defaults={
                    "product": product.get("product"),
                    "variant": variant,
                    "quantity": quantity
                }
            )
            if not created:
                # cart_item.quantity += quantity
                cart_item.save()

            results.append(cart_item)

        serializer = CartItemSerializer(results, many=True)

        return Response({
            "message": "Items added to cart successfully",
            "added_items": serializer.data,
            "cart_total": sum(item.total_price for item in _cart.items.all())
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        cart = self.get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response({"message": "Cart cleared"}, status=status.HTTP_200_OK)

