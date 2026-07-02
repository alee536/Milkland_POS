from django.contrib import admin
from apps.sales.models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'sale_date', 'sale_type', 'grand_total', 'paid_amount', 'balance_amount']
    list_filter = ['sale_type', 'sale_date']
    search_fields = ['invoice_number', 'customer__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SaleItemInline]


@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'sale_rate', 'line_total']
    search_fields = ['product__name', 'sale__invoice_number']
