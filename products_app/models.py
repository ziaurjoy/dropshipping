from django.db import models

class SettingExchangeRate(models.Model):
    code = models.CharField(max_length=10, unique=True)  # USD, BDT, CNY
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)  # $, ৳, ¥
    is_active = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.rate}"



class Category(models.Model):
    category_id = models.CharField(max_length=100, unique=True)  # e.g. "fashion_and_apparel"
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="subcategories"
    )
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "subcategories"
        ordering = ["id"]

    def __str__(self):
        return f"{self.category.name} → {self.name}"


class Item(models.Model):
    subcategory = models.ForeignKey(
        Subcategory, on_delete=models.CASCADE, related_name="items"
    )
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name