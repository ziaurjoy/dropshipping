from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        session_key = self.request.session.session_key
        if not session_key:
            self.request.session.create()
            session_key = self.request.session.session_key
        return Cart.objects.filter(session_key=session_key)

    def get_object(self):
        cart = self.get_queryset().first()
        if not cart:
            # Create new cart automatically
            if self.request.user.is_authenticated:
                cart = Cart.objects.create(user=self.request.user)
            else:
                cart = Cart.objects.create(session_key=self.request.session.session_key)
        return cart

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        """GET /api/cart/my_cart/ → returns current user's/guest's cart"""
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """POST /api/cart/add_item/ with {variant_id, quantity}"""
        variant_id = request.data.get('variant_id')
        quantity = int(request.data.get('quantity', 1))

        variant = get_object_or_404('products.ProductVariant', id=variant_id)
        cart = self.get_object()

        item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        """POST /api/cart/remove_item/ with {item_id}"""
        item_id = request.data.get('item_id')
        CartItem.objects.filter(id=item_id, cart=self.get_object()).delete()
        return Response({'status': 'removed'}, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        cart = self.request.query_params.get('cart')
        if cart:
            return CartItem.objects.filter(cart_id=cart)
        return super().get_queryset()