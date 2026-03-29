from django.db import models

# Create your models here.


import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from mptt.models import MPTTModel, TreeForeignKey

User = get_user_model()

# ====================== CATEGORY (Self-referencing MPTT tree) ======================
class Category(MPTTModel):
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    icon = models.ImageField(upload_to='categories/icons/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class MPTTMeta:
        order_insertion_by = ['sort_order', 'name']

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ====================== PRODUCT ======================
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=320)
    description = models.TextField(blank=True)
    source_url = models.URLField(null=True, blank=True)
    source_platform = models.CharField(max_length=50, blank=True)  # e.g. '1688', 'Alibaba'
    base_cost = models.DecimalField(max_digits=12, decimal_places=2, default=30.00)
    markup_percent = models.DecimalField(max_digits=6, decimal_places=2, default=30.00)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['is_active', 'created_at'])]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# ====================== PRODUCT VARIANT ======================
class ProductVariant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True)
    # size = models.CharField(max_length=50, null=True, blank=True)
    # color = models.CharField(max_length=50, null=True, blank=True)
    extra_attrs = models.JSONField(null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2)
    weight_grams = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['sku']

    def __str__(self):
        return f"{self.product.name} ({self.sku})"


# ====================== PRODUCT IMAGE ======================
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f"Image for {self.product.name}"


# ====================== WISHLIST ======================
class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ====================== REVIEW ======================
class Review(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()  # 1-5 (you can add validator if needed)
    body = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"


# ====================== SUPPLIER PRODUCT ======================
class SupplierProduct(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='supplier_products')
    supplier_name = models.CharField(max_length=100)
    supplier_sku = models.CharField(max_length=100)
    supplier_url = models.URLField(null=True, blank=True)
    cost_cny = models.DecimalField(max_digits=12, decimal_places=2)
    cost_bdt = models.DecimalField(max_digits=12, decimal_places=2)
    min_order_qty = models.PositiveIntegerField(default=1)
    lead_days = models.PositiveSmallIntegerField(default=7)
    last_synced = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.supplier_name} - {self.supplier_sku}"


# ====================== BANNER ======================
class Banner(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    image_desktop = models.ImageField(upload_to='banners/')
    image_mobile = models.ImageField(upload_to='banners/', null=True, blank=True)
    link_url = models.URLField(null=True, blank=True)
    placement = models.CharField(
        max_length=50,
        choices=[('homepage', 'Homepage'), ('category', 'Category'), ('flash', 'Flash')]
    )
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title