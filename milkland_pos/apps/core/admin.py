from django.contrib import admin
from apps.core.models import BusinessSettings


@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ['shop_name', 'tagline', 'contact_number', 'updated_at']
