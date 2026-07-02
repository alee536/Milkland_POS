from django.contrib import admin
from apps.finance.models import CustomerPayment, SupplierPayment, ExpenseCategory, Expense, Wastage


@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ['customer', 'payment_date', 'amount', 'payment_method', 'received_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['customer__name']
    readonly_fields = ['created_at']


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ['supplier', 'payment_date', 'amount', 'payment_method', 'paid_by']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['supplier__name']
    readonly_fields = ['created_at']


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'expense_date', 'description', 'added_by']
    list_filter = ['category', 'expense_date']
    search_fields = ['description']
    readonly_fields = ['created_at']


@admin.register(Wastage)
class WastageAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'wastage_date', 'reason', 'estimated_loss_amount', 'added_by']
    list_filter = ['wastage_date']
    search_fields = ['product__name', 'reason']
    readonly_fields = ['created_at']
