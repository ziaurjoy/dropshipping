
import re
from django.db import models
from django.conf import settings
from products_app.models import Product  # ← Change if your Product model is elsewhere


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


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


def calculate_total(items):
    total = 0
    breakdown = []

    for item in items:
        price_str = item.get("price", "")
        quantity = item.get("quantity", 0)

        # Extract numeric value (remove currency symbol)
        price = float(price_str.replace("৳", "").strip())

        item_total = price * quantity
        total += item_total

        breakdown.append({
            "size_name": item.get("size_name"),
            "unit_price": price,
            "quantity": quantity,
            "total": item_total
        })

    return {
        "items": breakdown,
        "grand_total": total
    }

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")

    product_id = models.CharField(max_length=100, blank=True, null=True)
    product = models.JSONField(blank=True, null=True)

    # variant_key = models.CharField(max_length=100, blank=True, null=True)
    variant = models.JSONField(blank=True, null=True)

    quantity = models.JSONField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product_id")
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.quantity} × {self.product.get('product', {}).get('title', 'Unknown')}"

    @property
    def total_price(self):
        variant = self.variant or {}

        # 🔒 handle list case safely
        if isinstance(variant, list):
            variant = variant[0] if variant else {}

        result = calculate_total(self.variant)
        return result["grand_total"]