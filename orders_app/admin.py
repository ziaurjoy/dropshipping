from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from orders_app.models import Order



import json
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import Order
from django.utils.safestring import mark_safe
from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ['id', 'order_number', 'user', 'product_name', 'status', 'total_price', 'created_at', 'view_button']
    list_filter     = ['status', 'shipping_method']
    search_fields   = ['order_number', 'product_name', 'user__email']
    readonly_fields = [
        'order_number', 'created_at', 'updated_at',
        'variants_pretty',
        'user_card',        # ← replaces user dropdown
        'address_card',     # ← replaces address dropdown
    ]

    fieldsets = (
        ('Order Info', {
            'fields': ('order_number', 'status', 'shipping_method', 'total_price')
        }),
        ('Customer', {
            'fields': ('user_card',)          # ← card instead of dropdown
        }),
        ('Delivery Address', {
            'fields': ('address_card',)       # ← card instead of dropdown
        }),
        ('Product', {
            'fields': ('product_id', 'product_name', 'product_image')
        }),
        ('Variants', {
            'fields': ('variants_pretty',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    # ── View button ───────────────────────────────────────────
    def view_button(self, obj):
        return mark_safe(
            f'<a class="button" href="{obj.id}/variants/" style="'
            f'background:#f97316;color:white;padding:4px 12px;'
            f'border-radius:4px;font-size:12px;text-decoration:none;'
            f'font-weight:600;">View Variants</a>'
        )
    view_button.short_description = 'Variants'

    # ── User card ─────────────────────────────────────────────
    # ── User card ─────────────────────────────────────────────
    def user_card(self, obj):
        if not obj.user:
            return mark_safe('<p style="color:#9ca3af">No user assigned.</p>')

        user    = obj.user
        exclude = {'password', 'last_login', 'is_superuser', 'groups', 'user_permissions'}
        fields  = [
            f for f in user._meta.get_fields()
            if hasattr(f, 'attname') and f.attname not in exclude
        ]

        rows = ''.join([
            f"""
            <tr>
                <td style="padding:7px 14px;font-weight:600;color:#374151;
                        font-size:12px;white-space:nowrap;border-bottom:1px solid #e5e7eb;
                        background:#f3f4f6;width:35%">
                    {f.verbose_name.title()}
                </td>
                <td style="padding:7px 14px;font-size:13px;color:#111827;
                        background:#ffffff;border-bottom:1px solid #e5e7eb">
                    {getattr(user, f.attname, '—') or '—'}
                </td>
            </tr>
            """
            for f in fields
        ])

        initial = str(user.get_full_name() or user.email or '?')[0].upper()

        return mark_safe(f"""
            <div style="border:1px solid #bae6fd;border-radius:10px;
                        overflow:hidden;max-width:600px;background:#ffffff">
                <!-- Header -->
                <div style="background:#0ea5e9;padding:14px 16px;
                            display:flex;align-items:center;gap:12px">
                    <div style="width:40px;height:40px;background:#ffffff;border-radius:50%;
                                display:flex;align-items:center;justify-content:center;
                                color:#0ea5e9;font-weight:700;font-size:18px;flex-shrink:0">
                        {initial}
                    </div>
                    <div>
                        <div style="font-weight:700;font-size:15px;color:#ffffff">
                            {user.get_full_name() or '—'}
                        </div>
                        <div style="font-size:12px;color:#e0f2fe;margin-top:2px">
                            {user.email}
                        </div>
                    </div>
                </div>
                <!-- Fields table -->
                <table style="width:100%;border-collapse:collapse;background:#ffffff">
                    {rows}
                </table>
            </div>
        """)

    user_card.short_description = 'Customer'


    # ── Address card ──────────────────────────────────────────
    def address_card(self, obj):
        if not obj.address:
            return mark_safe('<p style="color:#9ca3af">No address assigned.</p>')

        address = obj.address
        exclude = {'id', 'user_id'}
        fields  = [
            f for f in address._meta.get_fields()
            if hasattr(f, 'attname') and f.attname not in exclude
        ]

        rows = ''.join([
            f"""
            <tr>
                <td style="padding:7px 14px;font-weight:600;color:#374151;
                        font-size:12px;white-space:nowrap;border-bottom:1px solid #e5e7eb;
                        background:#f3f4f6;width:35%">
                    {f.verbose_name.title()}
                </td>
                <td style="padding:7px 14px;font-size:13px;color:#111827;
                        background:#ffffff;border-bottom:1px solid #e5e7eb">
                    {getattr(address, f.attname, '—') or '—'}
                </td>
            </tr>
            """
            for f in fields
        ])

        is_primary = getattr(address, 'is_primary', False)

        return mark_safe(f"""
            <div style="border:1px solid #bbf7d0;border-radius:10px;
                        overflow:hidden;max-width:600px;background:#ffffff">
                <!-- Header -->
                <div style="background:#16a34a;padding:14px 16px;
                            display:flex;align-items:center;gap:12px">
                    <div style="width:40px;height:40px;background:#ffffff;border-radius:50%;
                                display:flex;align-items:center;justify-content:center;flex-shrink:0">
                        <span style="font-size:20px">📍</span>
                    </div>
                    <div>
                        <div style="font-weight:700;font-size:15px;color:#ffffff">
                            Delivery Address
                            {'<span style="background:#ffffff;color:#16a34a;font-size:10px;font-weight:700;padding:2px 8px;border-radius:10px;margin-left:8px">Primary</span>' if is_primary else ''}
                        </div>
                        <div style="font-size:12px;color:#dcfce7;margin-top:2px">
                            {getattr(address, 'city', '') or ''}
                            {getattr(address, 'country', '') or ''}
                        </div>
                    </div>
                </div>
                <!-- Fields table -->
                <table style="width:100%;border-collapse:collapse;background:#ffffff">
                    {rows}
                </table>
            </div>
        """)

    address_card.short_description = 'Delivery Address'

    # ── Variants pretty ───────────────────────────────────────
    def variants_pretty(self, obj):
        variants = obj.variants or []
        rows     = []

        for entry in variants:
            variant     = entry.get('variant', {})
            quantity    = entry.get('quantity', {})
            weight_info = variant.get('weightInfo', {})

            sizes_html = ''.join([
                f"""
                <tr>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6">{s.get('size_name', '—')}</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6">৳{s.get('price', '0')}</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6">{s.get('stock', '0')}</td>
                    <td style="padding:8px 12px;border-bottom:1px solid #f3f4f6;font-weight:700;color:#f97316">
                        × {quantity.get(s.get('size_name', ''), 0)}
                    </td>
                </tr>
                """
                for s in variant.get('sizes', [])
            ])

            rows.append(f"""
                <div style="border:1px solid #e5e7eb;border-radius:10px;margin-bottom:16px;overflow:hidden">
                    <div style="background:#fff7ed;padding:12px 16px;display:flex;
                                align-items:center;gap:12px;border-bottom:1px solid #fed7aa">
                        <img src="{variant.get('image', '')}"
                             style="width:48px;height:48px;object-fit:cover;
                                    border-radius:8px;border:1px solid #fed7aa"
                             onerror="this.style.display='none'"/>
                        <div>
                            <div style="font-weight:600;font-size:14px;color:#1f2937">
                                {variant.get('color_name', '—')}
                            </div>
                            <div style="font-size:12px;color:#6b7280;margin-top:2px">
                                ⚖️ {variant.get('weightKg', 0)} kg &nbsp;|&nbsp;
                                📦 {weight_info.get('length', '—')} ×
                                   {weight_info.get('width', '—')} ×
                                   {weight_info.get('height', '—')} cm
                            </div>
                        </div>
                    </div>

                    <table style="width:100%;border-collapse:collapse;font-size:13px">
                        <thead>
                            <tr style="background:#f9fafb">
                                <th style="padding:8px 12px;text-align:left;color:#6b7280;font-weight:600">Size</th>
                                <th style="padding:8px 12px;text-align:left;color:#6b7280;font-weight:600">Price</th>
                                <th style="padding:8px 12px;text-align:left;color:#6b7280;font-weight:600">Stock</th>
                                <th style="padding:8px 12px;text-align:left;color:#6b7280;font-weight:600">Qty</th>
                            </tr>
                        </thead>
                        <tbody>{sizes_html}</tbody>
                    </table>

                    <div style="background:#f9fafb;padding:8px 12px;font-size:11px;
                                color:#9ca3af;border-top:1px solid #f3f4f6">
                        SKU: {weight_info.get('skuId', '—')} &nbsp;|&nbsp;
                        {weight_info.get('weight', '—')}g &nbsp;|&nbsp;
                        Vol: {weight_info.get('volume', '—')} cm³
                    </div>
                </div>
            """)

        return mark_safe(f'<div style="max-width:700px">{"".join(rows)}</div>')

    variants_pretty.short_description = 'Variants'

    # ── Variants popup page ───────────────────────────────────
    def get_urls(self):
        from django.urls import path
        urls   = super().get_urls()
        custom = [
            path(
                '<int:order_id>/variants/',
                self.admin_site.admin_view(self.variants_view),
                name='order_variants'
            ),
        ]
        return custom + urls

    # def variants_view(self, request, order_id):
    #     from django.shortcuts import get_object_or_404
    #     from django.template.response import TemplateResponse
    #     order   = get_object_or_404(Order, id=order_id)
    #     context = {
    #         **self.admin_site.each_context(request),
    #         'order':    order,
    #         'variants': order.variants or [],
    #         'title':    f'Variants — {order.order_number}',
    #     }
    #     return TemplateResponse(request, 'admin/order_variants.html', context)

    def variants_view(self, request, order_id):
        from django.shortcuts import get_object_or_404
        from django.template.response import TemplateResponse
        order = get_object_or_404(Order, id=order_id)

        product_url = (
            f"https://detail.1688.com/offer/{order.product_id}.html"
            if order.product_id else None
        )

        context = {
            **self.admin_site.each_context(request),
            'order':       order,
            'variants':    order.variants or [],
            'product_url': product_url,
            'title':       f'Variants — {order.order_number}',
        }
        return TemplateResponse(request, 'admin/order_variants.html', context)