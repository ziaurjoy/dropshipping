

from rest_framework import serializers
from products_app.models import Product
# from .models import CartItem, Cart

# If you don't have ProductMinimalSerializer yet, add this simple one:
class ProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price"]  # add image, etc. if you want


# class CartItemSerializer(serializers.ModelSerializer):
#     # product = ProductMinimalSerializer(read_only=True)
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = CartItem
#         fields = ["id", "product", "quantity", 'variant',  "total_price", "added_at"]

#     def get_total_price(self, obj):

#         return obj.total_price


# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)
#     total_price = serializers.SerializerMethodField()

#     class Meta:
#         model = Cart
#         fields = ["id", "items", "total_price", "created_at", "updated_at"]

#     def get_total_price(self, obj):
#         return obj.total_price






# from rest_framework import serializers
# from .models import CartItem, CartVariant, CartVariantSize


# class CartVariantSizeSerializer(serializers.Serializer):
#     size_name = serializers.CharField()
#     price     = serializers.DecimalField(max_digits=10, decimal_places=2)
#     stock     = serializers.CharField()  # comes as string from frontend


# class WeightInfoSerializer(serializers.Serializer):
#     skuId  = serializers.IntegerField()
#     sku1   = serializers.CharField()
#     weight = serializers.FloatField()
#     length = serializers.FloatField()
#     width  = serializers.FloatField()
#     height = serializers.FloatField()
#     volume = serializers.FloatField()


# class CartVariantSerializer(serializers.Serializer):
#     color_name  = serializers.CharField()
#     image       = serializers.URLField()
#     weightKg    = serializers.FloatField()
#     weightInfo  = WeightInfoSerializer()
#     sizes       = CartVariantSizeSerializer(many=True)


# class AddToCartSerializer(serializers.Serializer):
#     product_id      = serializers.CharField()
#     variant         = CartVariantSerializer()
#     quantity        = serializers.DictField(child=serializers.IntegerField())  # {"Standard": 1}
#     shipping_method = serializers.ChoiceField(choices=['air', 'sea'])

#     def create(self, validated_data):
#         user            = self.context['request'].user
#         variant_data    = validated_data['variant']
#         weight_info     = variant_data['weightInfo']
#         quantity_map    = validated_data['quantity']
#         sizes_data      = variant_data['sizes']

#         # ── Create or update CartItem ─────────────────────────
#         cart_item, _ = NewCartItem.objects.update_or_create(
#             user=user,
#             product_id=validated_data['product_id'],
#             defaults={
#                 'shipping_method': validated_data['shipping_method'],
#             }
#         )

#         # ── Create or update CartVariant ──────────────────────
#         cart_variant, _ = CartVariant.objects.update_or_create(
#             cart_item=cart_item,
#             defaults={
#                 'color_name': variant_data['color_name'],
#                 'image':      variant_data['image'],
#                 'weight_kg':  variant_data['weightKg'],
#                 'sku_id':     weight_info['skuId'],
#                 'sku1':       weight_info['sku1'],
#                 'weight':     weight_info['weight'],
#                 'length':     weight_info['length'],
#                 'width':      weight_info['width'],
#                 'height':     weight_info['height'],
#                 'volume':     weight_info['volume'],
#             }
#         )

#         # ── Create or update CartVariantSize ──────────────────
#         for size in sizes_data:
#             qty = quantity_map.get(size['size_name'], 0)
#             CartVariantSize.objects.update_or_create(
#                 variant=cart_variant,
#                 size_name=size['size_name'],
#                 defaults={
#                     'price':    size['price'],
#                     'stock':    int(size['stock']),
#                     'quantity': qty,
#                 }
#             )

#         return cart_item


# class CartItemResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = NewCartItem
#         fields = ['id', 'product_id', 'shipping_method', 'created_at', 'updated_at']



# class CartVariantSizeResponseSerializer(serializers.ModelSerializer):
#     class Meta:
#         model  = CartVariantSize
#         fields = ['id', 'size_name', 'price', 'stock', 'quantity']


# class CartVariantResponseSerializer(serializers.ModelSerializer):
#     sizes = CartVariantSizeResponseSerializer(many=True)

#     class Meta:
#         model  = CartVariant
#         fields = [
#             'id', 'color_name', 'image',
#             'weight_kg', 'sku_id', 'sku1',
#             'weight', 'length', 'width', 'height', 'volume',
#             'sizes',
#         ]


# class CartItemResponseSerializer(serializers.ModelSerializer):
#     variant = CartVariantResponseSerializer()

#     class Meta:
#         model  = NewCartItem
#         fields = [
#             'id', 'product_id', 'shipping_method',
#             'variant', 'created_at', 'updated_at',
#         ]



from rest_framework import serializers
from .models import Cart


class CartSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model  = Cart
        fields = [
            'id',
            'user',
            'product_id',
            'product_name',
            'product_image',
            'variants',           # raw JSON in, raw JSON out
            'shipping_method',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        user = self.context['request'].user

        # update if same product already in cart, else create
        cart, _ = Cart.objects.update_or_create(
            user=user,
            product_id=validated_data['product_id'],
            defaults={
                'product_name':    validated_data['product_name'],
                'product_image':   validated_data['product_image'],
                'variants':        validated_data['variants'],
                'shipping_method': validated_data['shipping_method'],
            }
        )
        return cart