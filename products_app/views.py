from django.shortcuts import render

# Create your views here.


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    Category, Product, ProductVariant, ProductImage,
    Wishlist, Review, SupplierProduct, Banner
)
from .serializers import (
    CategorySerializer, ProductListSerializer, ProductDetailSerializer,
    ProductVariantSerializer, ProductImageSerializer,
    WishlistSerializer, ReviewSerializer,
    SupplierProductSerializer, BannerSerializer
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('images', 'variants', 'supplier_products', 'reviews').select_related('category')
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'variants__selling_price']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        product = self.get_object()
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return Response({'status': 'added to wishlist'}, status=status.HTTP_201_CREATED)


# ====================== PRODUCT VARIANT VIEWSET (NEW) ======================
class ProductVariantViewSet(viewsets.ModelViewSet):
    # ... existing code ...
    queryset = ProductVariant.objects.select_related('product')
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAdminUser]
        # Optional: filter by product if 'product' query param is provided
    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset

    def perform_create(self, serializer):
        # Optional: auto-link to product if created via nested route
        product_id = self.request.query_params.get('product') or self.kwargs.get('product_pk')
        if product_id:
            product = get_object_or_404(Product, pk=product_id)
            serializer.save(product=product)
        else:
            serializer.save()

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BannerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Banner.objects.filter(is_active=True)
    serializer_class = BannerSerializer


# Extra lightweight endpoints if you don't want full ModelViewSet
class SupplierProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SupplierProduct.objects.all()
    serializer_class = SupplierProductSerializer