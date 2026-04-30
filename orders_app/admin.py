from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Coupon, Order, OrderItem, Payment, ShipmentSetting, ShippingZone, Shipment, SupportTicket


# ─────────────────────────────────────────────
# Inlines
# ─────────────────────────────────────────────

# class OrderItemInline(admin.TabularInline):

#     model = OrderItem
#     extra = 0
#     readonly_fields = ('product_display', 'unit_price', 'quantity', 'total')
#     fields = ('product_display', 'unit_price', 'quantity', 'total')
#     can_delete = False

#     def has_add_permission(self, request, obj=None):
#         return False

#     @admin.display(description='Product')
#     def product_display(self, obj):
#         p = obj.product
#         if not p or not isinstance(p, dict):
#             return '—'

#         title = p.get('title') or p.get('product_name') or 'Unknown Product'
#         image = p.get('image', '')
#         price = p.get('price', {})

#         amount = price.get('amount', '') if isinstance(price, dict) else ''
#         currency = price.get('currency', '') if isinstance(price, dict) else ''
#         variant = p.get('variant') or {}
#         size = variant.get('size', '') if isinstance(variant, dict) else ''
#         color = variant.get('color', '') if isinstance(variant, dict) else ''
#         offer_id = p.get('offer_id', '')
#         url = p.get('url', '')

#         # Build variant badge
#         variant_html = ''
#         if size or color:
#             badges = ''
#             if color:
#                 badges += format_html(
#                     '<span style="background:#e0e7ff;color:#3730a3;padding:1px 8px;'
#                     'border-radius:10px;font-size:11px;margin-right:4px">🎨 {}</span>', color)
#             if size:
#                 badges += format_html(
#                     '<span style="background:#dcfce7;color:#166534;padding:1px 8px;'
#                     'border-radius:10px;font-size:11px">📐 {}</span>', size)
#             variant_html = format_html('<div style="margin-top:4px">{}</div>', badges)

#         # Build price display
#         price_html = ''
#         if amount:
#             price_html = format_html(
#                 '<div style="color:#6b7280;font-size:11px;margin-top:2px">'
#                 'Listed: {} {}</div>', currency, amount)

#         # Build offer ID / link
#         meta_html = ''
#         if offer_id:
#             if url:
#                 meta_html = format_html(
#                     '<div style="color:#9ca3af;font-size:10px;margin-top:3px">'
#                     'SKU: <a href="{}" target="_blank" style="color:#6366f1">{}</a></div>',
#                     url, offer_id)
#             else:
#                 meta_html = format_html(
#                     '<div style="color:#9ca3af;font-size:10px;margin-top:3px">SKU: {}</div>',
#                     offer_id)

#         # Image thumbnail
#         img_html = ''
#         if image:
#             img_html = format_html(
#                 '<img src="{}" style="width:52px;height:52px;object-fit:cover;'
#                 'border-radius:6px;margin-right:10px;flex-shrink:0;border:1px solid #e5e7eb">',
#                 image)

#         return format_html(
#             '<div style="display:flex;align-items:flex-start">'
#             '{img}'
#             '<div>'
#             '<div style="font-weight:600;font-size:13px;max-width:420px;line-height:1.4">{title}</div>'
#             '{variant}{price}{meta}'
#             '</div>'
#             '</div>',
#             img=img_html,
#             title=title,
#             variant=variant_html,
#             price=price_html,
#             meta=meta_html,
#         )

from django.utils.safestring import mark_safe
from django.utils.html import format_html

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_display', 'unit_price', 'quantity', 'total')
    fields = ('product_display', 'unit_price', 'quantity', 'total')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description='Product')
    def product_display(self, obj):
        p = obj.product
        if not p or not isinstance(p, dict):
            return '—'

        # ── Basic fields ──────────────────────────────────────────────────────
        title     = p.get('title') or p.get('product_name') or 'Unknown Product'
        image     = p.get('image', '')
        url       = p.get('url', '')
        offer_id  = p.get('offer_id', '')
        sold      = p.get('sold', '')
        rating    = p.get('rating', '')
        moq       = p.get('moq', '')

        # ── Original listed price (from product.price dict) ───────────────────
        price_info  = p.get('price', {}) or {}
        listed_amt  = price_info.get('amount', '') if isinstance(price_info, dict) else ''
        listed_cur  = price_info.get('currency', '') if isinstance(price_info, dict) else ''
        overseas    = price_info.get('overseas', '') if isinstance(price_info, dict) else ''

        # ── Variants (list of dicts with price, size_name, quantity, stock) ───
        variants = p.get('variant', [])
        if isinstance(variants, dict):        # guard: sometimes stored as dict
            variants = [variants]
        variants = variants if isinstance(variants, list) else []

        # ── Image ─────────────────────────────────────────────────────────────
        img_html = format_html(
            '<img src="{}" style="width:60px;height:60px;object-fit:cover;'
            'border-radius:8px;border:1px solid #e5e7eb;flex-shrink:0">',
            image
        ) if image else format_html(
            '<div style="width:60px;height:60px;border-radius:8px;background:#f3f4f6;'
            'display:flex;align-items:center;justify-content:center;'
            'color:#9ca3af;font-size:20px;flex-shrink:0">📦</div>'
        )

        # ── Title + link ──────────────────────────────────────────────────────
        if url:
            title_html = format_html(
                '<a href="{}" target="_blank" style="font-weight:700;font-size:13px;'
                'color:#1d4ed8;text-decoration:none;line-height:1.4;display:block;'
                'max-width:400px">{}</a>', url, title
            )
        else:
            title_html = format_html(
                '<span style="font-weight:700;font-size:13px;color:#111827;'
                'line-height:1.4;display:block;max-width:400px">{}</span>', title
            )

        # ── Meta badges row (rating, sold, moq) ──────────────────────────────
        badges_html = ''
        if rating:
            badges_html += format_html(
                '<span style="background:#fef9c3;color:#854d0e;padding:1px 7px;'
                'border-radius:8px;font-size:11px;margin-right:4px">⭐ {}</span>', rating
            )
        if sold:
            badges_html += format_html(
                '<span style="background:#f0fdf4;color:#166534;padding:1px 7px;'
                'border-radius:8px;font-size:11px;margin-right:4px">🛒 {}</span>', sold
            )
        if moq:
            badges_html += format_html(
                '<span style="background:#eff6ff;color:#1d4ed8;padding:1px 7px;'
                'border-radius:8px;font-size:11px">📦 {}</span>', moq
            )
        meta_badges_html = format_html(
            '<div style="margin-top:5px">{}</div>', mark_safe(badges_html)
        ) if badges_html else ''

        # ── Original price row ────────────────────────────────────────────────
        price_html = ''
        if listed_amt or overseas:
            price_html = format_html(
                '<div style="margin-top:4px;font-size:11px;color:#6b7280">'
                'Listed: <strong>{} {}</strong>'
                '{}'
                '</div>',
                listed_cur, listed_amt,
                format_html(' &nbsp;·&nbsp; <span style="color:#059669">{}</span>', overseas) if overseas else ''
            )

        # ── Variants table ────────────────────────────────────────────────────
        variants_html = ''
        if variants:
            rows = ''
            for v in variants:
                size_name = v.get('size_name', '—')
                v_price   = v.get('price', '—')
                v_qty     = v.get('quantity', '—')
                v_stock   = v.get('stock', '')
                stock_badge = format_html(
                    '<span style="color:#6b7280;font-size:10px">{}</span>', v_stock
                ) if v_stock else ''

                rows += format_html(
                    '<tr style="border-bottom:1px solid #f3f4f6">'
                    '<td style="padding:3px 8px;font-size:11px;font-weight:600;color:#374151">{size}</td>'
                    '<td style="padding:3px 8px;font-size:11px;color:#059669;font-weight:700">{price}</td>'
                    '<td style="padding:3px 8px;font-size:11px;color:#6b7280">qty: {qty} {stock}</td>'
                    '</tr>',
                    size=size_name, price=v_price, qty=v_qty, stock=stock_badge
                )
            variants_html = format_html(
                '<div style="margin-top:6px">'
                '<table style="border-collapse:collapse;background:#f9fafb;'
                'border-radius:6px;overflow:hidden;font-size:11px;width:auto">'
                '<thead><tr style="background:#f3f4f6">'
                '<th style="padding:3px 8px;text-align:left;color:#9ca3af;font-weight:600;font-size:10px">SIZE</th>'
                '<th style="padding:3px 8px;text-align:left;color:#9ca3af;font-weight:600;font-size:10px">PRICE</th>'
                '<th style="padding:3px 8px;text-align:left;color:#9ca3af;font-weight:600;font-size:10px">QTY</th>'
                '</tr></thead>'
                '<tbody>{}</tbody>'
                '</table></div>',
                mark_safe(rows)
            )

        # ── Offer ID / SKU ────────────────────────────────────────────────────
        sku_html = format_html(
            '<div style="margin-top:4px;font-size:10px;color:#9ca3af">'
            'SKU: <span style="font-family:monospace;color:#6366f1">{}</span></div>',
            offer_id
        ) if offer_id else ''

        # ── Assemble ──────────────────────────────────────────────────────────
        return format_html(
            '<div style="display:flex;align-items:flex-start;gap:12px;padding:4px 0">'
            '{img}'
            '<div style="flex:1">'
            '{title}'
            '{meta_badges}'
            '{price}'
            '{variants}'
            '{sku}'
            '</div>'
            '</div>',
            img=img_html,
            title=title_html,
            meta_badges=meta_badges_html,
            price=price_html,
            variants=variants_html,
            sku=sku_html,
        )

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    # All fields readonly — payments are recorded facts, not edited here
    readonly_fields = ('id', 'method', 'status', 'amount', 'transaction_id', 'gateway_ref', 'paid_at')
    fields = ('id', 'method', 'status', 'amount', 'transaction_id', 'gateway_ref', 'paid_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


class ShipmentInline(admin.StackedInline):
    model = Shipment
    extra = 0
    # 'order' excluded — it's the parent FK; 'id' excluded (UUID auto)
    readonly_fields = ('id', 'tracking_number', 'tracking_url', 'shipped_at', 'delivered_at', 'estimated_delivery')
    fields = ('id', 'carrier', 'status', 'tracking_number', 'tracking_url',
              'shipped_at', 'estimated_delivery', 'delivered_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
# Coupon
# ─────────────────────────────────────────────

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_order_amount',
                    'used_count', 'max_uses', 'valid_from', 'valid_until', 'is_active', 'usage_bar')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code',)
    list_editable = ('is_active',)
    ordering = ('-valid_until',)
    readonly_fields = ('used_count',)

    @admin.display(description='Usage')
    def usage_bar(self, obj):
        if obj.max_uses:
            pct = int((obj.used_count / obj.max_uses) * 100)
            color = 'red' if pct >= 90 else 'orange' if pct >= 60 else 'green'
            return format_html(
                '<div style="width:100px;background:#eee;border-radius:4px">'
                '<div style="width:{pct}%;background:{color};height:12px;border-radius:4px"></div>'
                '</div> {used}/{max}',
                pct=pct, color=color, used=obj.used_count, max=obj.max_uses
            )
        return f'{obj.used_count} / ∞'


# ─────────────────────────────────────────────
# Order
# ─────────────────────────────────────────────

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user_link', 'status_badge', 'subtotal',
                    'discount_amount', 'shipping_charge', 'total', 'coupon', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'user__email', 'user__phone')
    # Only actual model fields go here — NOT custom method names like status_badge/user_link
    readonly_fields = ('id', 'order_number', 'created_at', 'subtotal',
                       'discount_amount', 'shipping_charge', 'total')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, PaymentInline, ShipmentInline]
    raw_id_fields = ('user', 'coupon', 'address')
    list_per_page = 30

    fieldsets = (
        ('Order Info', {
            # All fields here must exist on the model or in readonly_fields
            'fields': ('id', 'order_number', 'user', 'address', 'status', 'notes', 'created_at')
        }),
        ('Financials', {
            'fields': ('subtotal', 'discount_amount', 'shipping_charge', 'total', 'coupon')
        }),
    )

    STATUS_COLORS = {
        'pending': '#f59e0b',
        'confirmed': '#3b82f6',
        'processing': '#8b5cf6',
        'shipped': '#06b6d4',
        'delivered': '#10b981',
        'cancelled': '#ef4444',
        'refunded': '#6b7280',
    }

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#999')
        return format_html(
            '<span style="background:{color};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">{status}</span>',
            color=color, status=obj.get_status_display()
        )

    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:users_app_user_change', args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user)


# ─────────────────────────────────────────────
# Payment
# ─────────────────────────────────────────────

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_link', 'method', 'status_badge', 'amount', 'transaction_id', 'paid_at')
    list_filter = ('method', 'status')
    search_fields = ('transaction_id', 'gateway_ref', 'order__order_number')
    readonly_fields = ('id', 'paid_at')
    raw_id_fields = ('order',)
    ordering = ('-paid_at',)

    fieldsets = (
        ('Payment Info', {
            'fields': ('id', 'order', 'method', 'status', 'amount')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'gateway_ref', 'paid_at')
        }),
    )

    STATUS_COLORS = {
        'pending': '#f59e0b',
        'success': '#10b981',
        'failed': '#ef4444',
        'refunded': '#6b7280',
    }

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#999')
        return format_html(
            '<span style="background:{color};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">{status}</span>',
            color=color, status=obj.get_status_display()
        )

    @admin.display(description='Order')
    def order_link(self, obj):
        url = reverse('admin:orders_app_order_change', args=[obj.order_id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)


# ─────────────────────────────────────────────
# ShippingZone
# ─────────────────────────────────────────────

@admin.register(ShippingZone)
class ShippingZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'standard_charge', 'express_charge', 'free_above', 'district_count')
    search_fields = ('name',)

    @admin.display(description='# Districts')
    def district_count(self, obj):
        return len(obj.districts) if isinstance(obj.districts, list) else '—'


# ─────────────────────────────────────────────
# Shipment
# ─────────────────────────────────────────────

@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'carrier', 'status_badge', 'tracking_number',
                    'tracking_link', 'shipped_at', 'estimated_delivery', 'delivered_at')
    list_filter = ('status', 'carrier')
    search_fields = ('tracking_number', 'order__order_number')
    readonly_fields = ('id', 'tracking_number', 'tracking_url', 'shipped_at', 'delivered_at', 'estimated_delivery')
    raw_id_fields = ('order',)
    ordering = ('-shipped_at',)

    fieldsets = (
        ('Shipment Info', {
            'fields': ('id', 'order', 'carrier', 'status')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'tracking_url')
        }),
        ('Dates', {
            'fields': ('shipped_at', 'estimated_delivery', 'delivered_at')
        }),
    )

    STATUS_COLORS = {
        'delivering': '#3b82f6',
        'out_for_delivery': '#f59e0b',
        'delivered': '#10b981',
        'returned': '#ef4444',
    }

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#999')
        return format_html(
            '<span style="background:{color};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">{status}</span>',
            color=color, status=obj.get_status_display()
        )

    @admin.display(description='Order')
    def order_link(self, obj):
        url = reverse('admin:orders_app_order_change', args=[obj.order_id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)

    @admin.display(description='Track')
    def tracking_link(self, obj):
        if obj.tracking_url:
            return format_html('<a href="{}" target="_blank">🔗 Track</a>', obj.tracking_url)
        return '—'


# ─────────────────────────────────────────────
# SupportTicket
# ─────────────────────────────────────────────

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'order_link', 'subject', 'status_badge', 'created_at', 'resolved_at')
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'user__email', 'order__order_number')
    readonly_fields = ('created_at', 'resolved_at')
    raw_id_fields = ('user', 'order')
    ordering = ('-created_at',)
    list_per_page = 30

    fieldsets = (
        ('Ticket Info', {
            'fields': ('user', 'order', 'subject', 'status')
        }),
        ('Message', {
            'fields': ('message',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'resolved_at'),
            'classes': ('collapse',),
        }),
    )

    STATUS_COLORS = {
        'open': '#ef4444',
        'in_progress': '#f59e0b',
        'resolved': '#10b981',
        'closed': '#6b7280',
    }

    actions = ['mark_resolved', 'mark_closed']

    @admin.display(description='Status')
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, '#999')
        return format_html(
            '<span style="background:{color};color:#fff;padding:2px 10px;'
            'border-radius:12px;font-size:12px;font-weight:600">{status}</span>',
            color=color, status=obj.get_status_display()
        )

    @admin.display(description='User')
    def user_link(self, obj):
        url = reverse('admin:users_app_user_change', args=[obj.user_id])
        return format_html('<a href="{}">{}</a>', url, obj.user)

    @admin.display(description='Order')
    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:orders_app_order_change', args=[obj.order_id])
            return format_html('<a href="{}">{}</a>', url, obj.order.order_number)
        return '—'

    @admin.action(description='Mark selected tickets as Resolved')
    def mark_resolved(self, request, queryset):
        updated = queryset.filter(status__in=['open', 'in_progress']).update(
            status='resolved', resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} ticket(s) marked as resolved.')

    @admin.action(description='Mark selected tickets as Closed')
    def mark_closed(self, request, queryset):
        updated = queryset.exclude(status='closed').update(status='closed')
        self.message_user(request, f'{updated} ticket(s) closed.')




@admin.register(ShipmentSetting)
class ShipmentSettingAdmin(admin.ModelAdmin):
    # list_display = ("label", "method", "price", "is_active", "priority")
    list_display = ("label", "method", "is_active", "priority")
    list_filter = ("method", "is_active")
    ordering = ("priority",)