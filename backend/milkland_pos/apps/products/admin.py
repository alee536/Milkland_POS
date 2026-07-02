from django.contrib import admin
from apps.products.models import Category, Product, StockAdjustment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'unit_type', 'purchase_price', 'sale_price', 'current_stock', 'is_active']
    list_filter = ['is_active', 'category', 'unit_type']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product', 'adjustment_type', 'quantity', 'reason', 'adjusted_by', 'adjustment_date']
    list_filter = ['adjustment_type', 'adjustment_date']
    search_fields = ['product__name', 'reason']
    readonly_fields = ['created_at']
