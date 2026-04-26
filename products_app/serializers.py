

from rest_framework import serializers
from .models import (Banner, Category, Product, ProductImage, ProductVariant, Review,
    SettingExchangeRate, SupplierProduct, Wishlist)


# class CategorySerializer(serializers.ModelSerializer):
#     children = serializers.SerializerMethodField()

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'slug', 'icon', 'is_active', 'sort_order', 'children']

#     def get_children(self, obj):
#         return CategorySerializer(obj.get_children(), many=True).data

class CategorySerializer(serializers.ModelSerializer):
    # Allow write of uploaded file for create/update
    icon = serializers.ImageField(required=False, allow_null=True)
    # Return an absolute full URL for responses
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'icon', 'is_active',
            'sort_order', 'parent', 'children'
        ]
        read_only_fields = ['id', 'slug', 'children']

    def get_icon(self, obj):
        """Always return full URL with domain"""
        if obj.icon:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None

    def get_children(self, obj):
        """Important: pass context so child icons also get full URL"""
        serializer = CategorySerializer(
            obj.get_children(),
            many=True,
            context=self.context
        )
        return serializer.data


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'

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


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name','category', 'slug', 'description', 'source_url',
            'source_platform', 'base_cost', 'markup_percent',
            'is_active', 'created_at'
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
        # fields = [
        #     'id', 'name', 'slug', 'description', 'source_url',
        #     'source_platform', 'base_cost', 'markup_percent',
        #     'is_active', 'created_at',
        #     'category', 'images', 'variants',
        #     'supplier_products', 'reviews'
        # ]

        depth = 1
        fields = '__all__'  # Include all fields, including related ones


# ── LIST SERIALIZER (lighter for catalog listing) ──
class ProductListSerializer(serializers.ModelSerializer):
    min_price = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        depth = 1

    def get_min_price(self, obj):
        variant = obj.variants.order_by('selling_price').first()
        return variant.selling_price if variant else None



class SettingExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SettingExchangeRate
        fields = '__all__'