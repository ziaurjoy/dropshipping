from cProfile import label

from django.db import models

# Create your models here.


import uuid
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
# from products_app.models import Product, ProductVariant
# from cart_app.models import Cart  # for easy order creation
from users_app.models import DeliveryAddress
from . import utils

User = get_user_model()


# class Address(models.Model):
#     """Address model (referenced by Order)."""
#     id = models.AutoField(primary_key=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
#     full_name = models.CharField(max_length=255)
#     phone = models.CharField(max_length=20)
#     address_line1 = models.CharField(max_length=255)
#     address_line2 = models.CharField(max_length=255, blank=True)
#     city = models.CharField(max_length=100)
#     district = models.CharField(max_length=100)   # for ShippingZone matching
#     postal_code = models.CharField(max_length=20, blank=True)
#     is_default = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.full_name} - {self.city}"




class Coupon(models.Model):
    """Discount coupons."""
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=[('flat', 'Flat'), ('percent', 'Percent')])
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True)
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateField()
    valid_until = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


import random

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    SHIPPING_CHOICES = [
        ('air', 'By Air'),
        ('sea', 'By Sea'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    # === Changed to 6-digit numeric order number ===
    order_number = models.CharField(
        max_length=6,
        unique=True,
        editable=False,
        help_text="6-digit order number (e.g., 784912)"
    )

    address = models.ForeignKey(
        DeliveryAddress,
        on_delete=models.PROTECT,
        blank=True,
        null=True
    )

    product_id = models.CharField(max_length=100)
    product_name = models.CharField(max_length=500)
    product_image = models.URLField(max_length=1000)
    variants = models.JSONField(default=list)

    shipping_method = models.CharField(
        max_length=10,
        choices=SHIPPING_CHOICES,
        default='air'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_unique_order_number()
        super().save(*args, **kwargs)

    def _generate_unique_order_number(self) -> str:
        """Generate a unique 6-digit numeric order number"""
        while True:
            # Generate 6-digit number (100000 to 999999)
            number = str(random.randint(100000, 999999))

            if not Order.objects.filter(order_number=number).exists():
                return number

    def __str__(self):
        return f"#{self.order_number} — {self.user} — {self.status}"

    # Helper property for frontend
    @property
    def display_order_number(self):
        return f"#{self.order_number}"




class Payment(models.Model):
    """Payment attempt/record. Supports bKash, Nagad, COD."""
    METHOD_CHOICES = [
        ('bkash', 'bKash'), ('nagad', 'Nagad'), ('rocket', 'Rocket'),
        ('card', 'Card'), ('cod', 'Cash on Delivery')
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    gateway_ref = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.method} - {self.order.order_number}"




class ShipmentSetting(models.Model):
    class ShipmentMethod(models.TextChoices):
        STANDARD = "standard", "Standard"
        EXPRESS = "express", "Express"
        SAME_DAY = "same_day", "Same Day"

    label = models.CharField(max_length=100)
    method = models.CharField(
        max_length=20,
        choices=ShipmentMethod.choices,
        default=ShipmentMethod.STANDARD
    )

    price = models.PositiveIntegerField(default=0)  # Flat charge for this shipping method
    price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days_min = models.PositiveIntegerField()
    estimated_days_max = models.PositiveIntegerField()

    icon = models.ImageField(upload_to='shipment_icons/', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority"]

    def __str__(self):
        return f"{self.label} ({self.method})"



class ShippingZone(models.Model):
    """Maps districts to shipping charge. Dhaka vs outside."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    districts = models.JSONField()          # list of district names
    standard_charge = models.DecimalField(max_digits=10, decimal_places=2)
    express_charge = models.DecimalField(max_digits=10, decimal_places=2)
    free_above = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name


class Shipment(models.Model):
    """Tracks physical shipment via SkyShip or 3PL."""

    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('RESCHEDULED', 'Rescheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipment')
    carrier = models.CharField(max_length=50, blank=True)   # SkyShip, Pathao, etc.
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    tracking_url = models.URLField(blank=True, null=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', db_index=True)

    def __str__(self):
        return f"Shipment for {self.order.order_number}"

    def save(self, *args, **kwargs):
        # Auto-generate tracking info only on first creation
        if not self.tracking_number:
            self.tracking_number = utils.generate_tracking_number(self)
            self.tracking_url = utils.generate_tracking_url(self)

        # Auto set estimated_delivery (e.g., 7 days from now)
        if not self.estimated_delivery:
            self.estimated_delivery = timezone.now().date() + timezone.timedelta(days=7)

        # Auto set shipped_at
        if self.status in ['delivering', 'out_for_delivery'] and not self.shipped_at:
            self.shipped_at = timezone.now()

        # Auto set delivered_at
        if self.status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()

        super().save(*args, **kwargs)


class SupportTicket(models.Model):

    """Customer support requests tied to an order."""

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"








