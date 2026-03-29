

from rest_framework import serializers
from .models import (
    Category, Product, ProductVariant, ProductImage,
    Wishlist, Review, SupplierProduct, Banner
)


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon', 'is_active', 'sort_order', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.get_children(), many=True).data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']

class DynamicAttributeField(serializers.JSONField):
    """Custom field that accepts any key-value dict"""
    def to_representation(self, value):
        return value or {}

class ProductVariantSerializer(serializers.ModelSerializer):
    # Flattened dynamic attributes (read-only for listing)
    attributes = serializers.SerializerMethodField()

    # Allow any JSON for extra_attrs on write
    extra_attrs = DynamicAttributeField(required=False, allow_null=True)

    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'size', 'color', 'extra_attrs',
            'attributes',           # ← new clean dynamic dict
            'stock_quantity', 'selling_price', 'weight_grams'
        ]
        read_only_fields = ['id']

    def get_attributes(self, obj):
        return obj.attributes

    # Optional: Validate that SKU is unique per product
    def validate(self, data):
        sku = data.get('sku')
        product = self.context.get('product')  # passed from nested view
        if sku and ProductVariant.objects.filter(product=product, sku=sku).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError({"sku": "This SKU already exists for this product."})
        return data


class SupplierProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierProduct
        fields = [
            'id', 'supplier_name', 'supplier_sku', 'supplier_url',
            'cost_cny', 'cost_bdt', 'min_order_qty', 'lead_days', 'last_synced'
        ]


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Review
        fields = ['id', 'user', 'rating', 'body', 'is_approved', 'created_at']


class WishlistSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'added_at']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = [
            'id', 'title', 'image_desktop', 'image_mobile',
            'link_url', 'placement', 'sort_order', 'is_active'
        ]


# ── DETAILED PRODUCT SERIALIZER (used for /products/<slug>/) ──
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    supplier_products = SupplierProductSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'source_url',
            'source_platform', 'base_cost', 'markup_percent',
            'is_active', 'created_at',
            'category', 'images', 'variants',
            'supplier_products', 'reviews'
        ]


# ── LIST SERIALIZER (lighter for catalog listing) ──
class ProductListSerializer(serializers.ModelSerializer):
    primary_image = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'primary_image',
            'min_price', 'is_active', 'created_at'
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first()
        return img.image.url if img else None

    def get_min_price(self, obj):
        variant = obj.variants.order_by('selling_price').first()
        return variant.selling_price if variant else None