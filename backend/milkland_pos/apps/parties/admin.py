from django.contrib import admin
from apps.parties.models import Customer, Supplier


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'current_balance', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'phone']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'current_balance', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'phone']
