from django.contrib import admin
from apps.purchases.models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'purchase_date', 'total_amount', 'paid_amount', 'payment_status']
    list_filter = ['payment_status', 'purchase_date']
    search_fields = ['invoice_number', 'supplier__name']
    readonly_fields = ['created_at', 'updated_at', 'remaining_amount', 'payment_status']
    inlines = [PurchaseItemInline]


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['purchase', 'product', 'quantity', 'purchase_rate', 'line_total']
    search_fields = ['product__name', 'purchase__invoice_number']
