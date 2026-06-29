
import re
from django.db import models
from django.conf import settings
# from products_app.models import Product  # ← Change if your Product model is elsewhere


# class Cart(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="cart"
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Cart of {self.user.username}"

#     @property
#     def total_price(self):
#         return sum(item.total_price for item in self.items.all())


# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
#     # product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     product = models.JSONField(blank=True, null=True)  # Store product details as JSON
#     variant = models.JSONField(blank=True, null=True)  # Store variant details as JSON
#     quantity = models.PositiveIntegerField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("cart", "product", "variant")
#         ordering = ["-added_at"]

#     def __str__(self):
#         return f"{self.quantity} × {self.product.name}"

#     @property
#     def total_price(self):
#         print('Calculating total price for CartItem:', self.product, self.variant, self.quantity)
#         unit_price = self.variant.get('price', 0)
#         currency = unit_price[0]
#         amount = unit_price[1:]
#         total_amount = float(amount) * self.quantity
#         return total_amount


# def calculate_total(items):
#     total = 0
#     breakdown = []

#     for item in items:
#         price_str = item.get("price", "")
#         quantity = item.get("quantity", 0)

#         # Extract numeric value (remove currency symbol)
#         price = float(price_str.replace("৳", "").strip())

#         item_total = price * quantity
#         total += item_total

#         breakdown.append({
#             "size_name": item.get("size_name"),
#             "unit_price": price,
#             "quantity": quantity,
#             "total": item_total
#         })

#     return {
#         "items": breakdown,
#         "grand_total": total
#     }

# class CartItem(models.Model):
#     cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

#     product_id = models.CharField(max_length=100, blank=True, null=True)
#     product = models.JSONField(blank=True, null=True)

#     # variant_key = models.CharField(max_length=100, blank=True, null=True)
#     variant = models.JSONField(blank=True, null=True)

#     quantity = models.JSONField(default=1)
#     added_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ("cart", "product_id")
#         ordering = ["-added_at"]

#     def __str__(self):
#         return f"{self.quantity} × {self.product.get('product', {}).get('title', 'Unknown')}"

#     @property
#     def total_price(self):
#         variant = self.variant or {}

#         # 🔒 handle list case safely
#         if isinstance(variant, list):
#             variant = variant[0] if variant else {}

#         result = calculate_total(self.variant)
#         return result["grand_total"]




# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class NewCartItem(models.Model):
#     SHIPPING_CHOICES = [
#         ('air', 'By Air'),
#         ('sea', 'By Sea'),
#     ]

#     user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
#     product_id      = models.CharField(max_length=100)
#     shipping_method = models.CharField(max_length=10, choices=SHIPPING_CHOICES, default='air')
#     created_at      = models.DateTimeField(auto_now_add=True)
#     updated_at      = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.user} - {self.product_id}"


# class CartVariant(models.Model):
#     cart_item  = models.OneToOneField(NewCartItem, on_delete=models.CASCADE, related_name='variant')
#     color_name = models.CharField(max_length=100)
#     image      = models.URLField()
#     weight_kg  = models.FloatField(default=0)

#     # weightInfo fields
#     sku_id  = models.BigIntegerField()
#     sku1    = models.CharField(max_length=100)
#     weight  = models.FloatField()   # grams
#     length  = models.FloatField()
#     width   = models.FloatField()
#     height  = models.FloatField()
#     volume  = models.FloatField()

#     def __str__(self):
#         return f"{self.cart_item} - {self.color_name}"


# class CartVariantSize(models.Model):
#     variant   = models.ForeignKey(CartVariant, on_delete=models.CASCADE, related_name='sizes')
#     size_name = models.CharField(max_length=100)
#     price     = models.DecimalField(max_digits=10, decimal_places=2)
#     stock     = models.IntegerField()
#     quantity  = models.IntegerField(default=0)  # from quantity map

#     def __str__(self):
#         return f"{self.variant} - {self.size_name}"





from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Cart(models.Model):
    SHIPPING_CHOICES = [
        ('air', 'By Air'),
        ('sea', 'By Sea'),
    ]

    user            = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product_id      = models.CharField(max_length=100)
    product_name    = models.CharField(max_length=500)
    product_image   = models.URLField(max_length=1000)
    variants        = models.JSONField(default=list)   # store entire variants array as-is
    shipping_method = models.CharField(max_length=10, choices=SHIPPING_CHOICES, default='air')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.product_name[:50]}"