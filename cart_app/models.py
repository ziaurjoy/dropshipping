from django.db import models

# Create your models here.

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from products_app.models import ProductVariant

User = get_user_model()


class Cart(models.Model):
    """One active cart per user (or session for guests)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts'
    )
    session_key = models.CharField(max_length=255, null=True, blank=True)
    coupon = models.ForeignKey(
        'orders_app.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts_coupon',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(user__isnull=False),
                name='unique_user_cart',
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                condition=models.Q(session_key__isnull=False),
                name='unique_session_cart',
            ),
        ]

    def __str__(self):
        return f"Cart {self.id} ({self.user or self.session_key})"


class CartItem(models.Model):
    """Line item inside a cart."""
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'variant')
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity} × {self.variant.sku}"

    @property
    def line_total(self):
        return self.variant.selling_price * self.quantity