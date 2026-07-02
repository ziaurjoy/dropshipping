import copy
import re
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.core.cache import cache

from products_app.models import SettingExchangeRate, Category, Subcategory, Item
from products_app.serializers import SettingExchangeRateSerializer
from products_app.services import (
    get_category_from_fastapi,
    get_products_details_from_fastapi,
    get_products_from_fastapi
)


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
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def list(self, request):
        cache_key = f"product_list_1688_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        print('cache_key:', cache_key)
        print('cached_data:', cached_data)
        if cached_data is not None:
            return Response(cached_data)

        data = get_products_from_fastapi(request=request)
        rate = SettingExchangeRate.objects.filter(code='BDT').first().rate
        converted = convert_list_currency_to_bdt(data, cny_to_bdt_rate=rate)

        cache.set(cache_key, converted, timeout=3600)  # Cache for 1 hour
        return Response(converted)

    def retrieve(self, request, pk=None):
        print('Retrieving product details for ID:', pk)
        cache_key = f"product_detail_1688_{pk}_{request.GET.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            return Response(cached_data)

        data = get_products_details_from_fastapi(product_id=pk, request=request)
        cny_to_bdt_rate = SettingExchangeRate.objects.all().filter(code='BDT').first().rate
        converted = convert_currency_to_bdt(data, cny_to_bdt_rate=cny_to_bdt_rate)

        cache.set(cache_key, converted, timeout=3600)  # Cache for 1 hour
        return Response(converted)


class Categories1688ViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def list(self, request):
        data = get_category_from_fastapi(request=request)
        return Response(data)


class SettingExchangeRateViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = SettingExchangeRate.objects.all().order_by('-created_at')
    serializer_class = SettingExchangeRateSerializer


class CategoryViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def list(self, request):
        categories_qs = Category.objects.prefetch_related('subcategories__items').all()
        categories_data = []
        for cat in categories_qs:
            subcategories_data = []
            for sub in cat.subcategories.all():
                items_data = []
                for item in sub.items.all():
                    items_data.append({
                        "name": item.name
                    })
                subcategories_data.append({
                    "name": sub.name,
                    "items": items_data
                })
            categories_data.append({
                "id": cat.category_id,
                "name": cat.name,
                "icon": cat.icon,
                "subcategories": subcategories_data
            })

        response_data = {
            "_id": "69df35f13c51f8b91387d4e2",
            "source": "1688.com",
            "total_categories": len(categories_data),
            "categories": categories_data
        }
        return Response(response_data)
