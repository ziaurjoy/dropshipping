from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import Cart

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display  = ['id', 'user', 'product_id', 'product_name', 'shipping_method', 'created_at']
    list_filter   = ['shipping_method']
    search_fields = ['product_id', 'product_name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']