from django.db import models


class BusinessSettings(models.Model):
    shop_name = models.CharField(max_length=200, default='MILK LAND')
    tagline = models.CharField(max_length=300, default='A Satluj Dairies Venture')
    service_highlight = models.CharField(max_length=300, default='Free Home Delivery')
    address = models.TextField(default='Commercial Market, New City, Bahawalnagar')
    contact_number = models.CharField(max_length=50, default='+923215307273')
    receipt_footer_message = models.TextField(default='Pure Dairy, Fresh Taste, Delivered to Your Doorstep.')
    currency_symbol = models.CharField(max_length=10, default='PKR')
    low_stock_alert_enabled = models.BooleanField(default=True)
    receipt_logo = models.ImageField(upload_to='settings/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Business Settings'
        verbose_name_plural = 'Business Settings'

    def __str__(self):
        return self.shop_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
