from django.shortcuts import render

# Create your views here.


from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import rest_framework.permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from products_app.permissions import IsReadOnlyForRegularUsers, RBACPermission
from products_app.permissions import IsReadOnlyForRegularUsers
from products_app.services import (get_category_from_fastapi, get_products_details_from_fastapi,
    get_products_from_fastapi)
from .models import (Banner, Category, Product, ProductImage, ProductVariant, Review,
    SettingExchangeRate, SupplierProduct, Wishlist)
from .serializers import (BannerSerializer, CategorySerializer, ProductDetailSerializer,
    ProductImageSerializer, ProductListSerializer, ProductSerializer, ProductVariantSerializer,
    ReviewSerializer, SettingExchangeRateSerializer, SupplierProductSerializer, WishlistSerializer)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [RBACPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        if self.action =='list':
            return super().get_queryset().filter(
                parent__isnull=True
            ).order_by('sort_order', 'name')
        return super().get_queryset().order_by('sort_order', 'name')


    # def get_permissions(self):
    #     """Only admins can create/update/delete categories"""
    #     if self.action in ['create', 'update', 'partial_update', 'destroy']:
    #         return [permissions.IsAdminUser()]
    #     return [permissions.IsAuthenticatedOrReadOnly()]


class ProductViewSet(viewsets.ModelViewSet):
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [RBACPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    queryset = Product.objects.prefetch_related('images', 'variants', 'supplier_products', 'reviews').select_related('category')
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'variants__selling_price']
    lookup_field = 'slug'



    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ProductSerializer
        return ProductDetailSerializer

    def perform_create(self, serializer):
        product = serializer.save()

        uploaded_image = self.request.FILES.get('image')
        alt_text = self.request.data.get('alt_text', 'Product image')

        if uploaded_image:
            ProductImage.objects.create(
                product=product,
                image=uploaded_image,
                alt_text=alt_text,
                is_primary=True,
                sort_order=0
            )


    def perform_update(self, serializer):
        product = serializer.save()

        uploaded_image = self.request.FILES.get('image')
        alt_text = self.request.data.get('alt_text', 'Product image')
        print('uploaded_image', uploaded_image)
        if uploaded_image:
            print('uploaded_image', uploaded_image)
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
            ProductImage.objects.create(
                product=product,
                image=uploaded_image,
                alt_text=alt_text,
                is_primary=True,
                sort_order=0
            )





    # def get_permissions(self):
    #     if self.action in ['create', 'update', 'partial_update', 'destroy']:
    #         return [permissions.IsAdminUser()]
    #     return [permissions.IsAuthenticatedOrReadOnly()]

    @action(detail=True, methods=['post'])
    def add_to_wishlist(self, request, pk=None):
        product = self.get_object()
        Wishlist.objects.get_or_create(user=request.user, product=product)
        return Response({'status': 'added to wishlist'}, status=status.HTTP_201_CREATED)




import copy, re

def convert_currency_to_bdt(data: dict, cny_to_bdt_rate: float = 16.5) -> dict:
    """
    Converts all CNY (¥/￥) currency fields to BDT (৳).
    Handles both:
      - raw product dict   →  {"price": ..., "details": ...}
      - wrapped response   →  {"updated": True, "product": {...}}
    """
    cny_to_bdt_rate = float(cny_to_bdt_rate)
    data = copy.deepcopy(data)
    USD_TO_BDT = 110.0

    # auto-detect wrapper
    product = data.get("product", data)

    def replace_cny(text: str) -> str:
        return re.sub(
            r'[¥￥]\s*\n?\s*(\d+)\s*\n?\s*(\.?\d*)',
            lambda m: f"৳{float(m.group(1) + (m.group(2) or '')) * cny_to_bdt_rate:.2f}",
            str(text)
        )

    # 1. top-level price
    p = product.get("price", {})
    if p:
        raw = re.sub(r'[^\d.]', '', (p.get("amount", "") + p.get("unit", "")))
        if raw:
            p["currency"] = "৳"
            p["amount"]   = f"{float(raw) * cny_to_bdt_rate:.2f}"
            p["unit"]     = ""
        overseas = p.get("overseas", "")
        if overseas:
            usd = re.sub(r'[^\d.]', '', overseas)
            p["overseas"] = f"৳{float(usd) * USD_TO_BDT:.2f}" if usd else overseas

    # 2. cart
    cart = (product.get("details", {})
                   .get("extract_product_title_and_cart", {})
                   .get("cart", {}))
    if cart:
        cart["price_range"] = replace_cny(cart.get("price_range", ""))
        cart["min_order"]   = replace_cny(cart.get("min_order", ""))
        for sku in cart.get("skus", []):
            if sku.get("price"):
                sku["price"] = replace_cny(sku["price"])

    # 3. variants
    for variant in product.get("details", {}).get("extract_product_variants", []):
        for size in variant.get("sizes", []):
            if size.get("price"):
                size["price"] = replace_cny(size["price"])

    return data


def convert_list_currency_to_bdt(data, cny_to_bdt_rate: float = 16.5):
    """
    Handles all possible shapes returned by the list API:
      - plain list:          [{...}, {...}]
      - paginated wrapper:   { "results": [...], "total": 100 }
      - other wrappers:      { "products": [...] }  /  { "items": [...] }
    """
    if isinstance(data, list):
        return [convert_currency_to_bdt(item, cny_to_bdt_rate) for item in data]

    if isinstance(data, dict):
        data = copy.deepcopy(data)
        for key in ("results", "products", "items", "data"):
            if key in data and isinstance(data[key], list):
                data[key] = [convert_currency_to_bdt(item, cny_to_bdt_rate) for item in data[key]]
                return data
        # fallback: single product dict
        return convert_currency_to_bdt(data, cny_to_bdt_rate)

    return data

class ProductFrom1688ViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        data = get_products_from_fastapi(
            page=int(request.query_params.get('page', 0)),
            limit=int(request.query_params.get('limit', 20)),
            category=request.query_params.get('category'),
            search=request.query_params.get('search'),
            request=request
        )

        cny_to_bdt_rate = SettingExchangeRate.objects.all().filter(code='BDT').first().rate

        converted = convert_list_currency_to_bdt(data, cny_to_bdt_rate=cny_to_bdt_rate)
        return Response(converted)


    def retrieve(self, request, pk=None):
        print('Retrieving product details for ID:', pk)
        data = get_products_details_from_fastapi(product_id=pk, request=request)
        cny_to_bdt_rate = SettingExchangeRate.objects.all().filter(code='BDT').first().rate
        converted = convert_currency_to_bdt(data, cny_to_bdt_rate=cny_to_bdt_rate)

        return Response(converted)



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


class ProductImageViewSet(viewsets.ModelViewSet):
    # queryset = ProductImage.objects.select_related('product')
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

#     # def get_queryset(self):
#     #     qs = super().get_queryset()
#     #     product_id = self.request.query_params.get('product')
#     #     if product_id:
#     #         qs = qs.filter(product_id=product_id)
#     #     return qs

#     def perform_create(self, serializer):
#         serializer.save()

#         instance = serializer.instance
#         if instance.is_primary:
#             # Ensure only one primary image per product
#             ProductImage.objects.filter(product=instance.product).exclude(pk=instance.pk).update(is_primary=False)
#         return instance

#     def perform_update(self, serializer):
#         instance = serializer.save()
#         if instance.is_primary:
#             ProductImage.objects.filter(product=instance.product).exclude(pk=instance.pk).update(is_primary=False)
#         return instance






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



class Categories1688ViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        data = get_category_from_fastapi(
            request=request
        )
        return Response(data)



class SettingExchangeRateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SettingExchangeRate.objects.all().order_by('-created_at')
    serializer_class = SettingExchangeRateSerializer
