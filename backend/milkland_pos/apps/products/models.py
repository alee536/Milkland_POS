from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('KG', 'KG'),
        ('Gram', 'Gram'),
        ('Litre', 'Litre'),
        ('Piece', 'Piece'),
        ('Jar', 'Jar'),
        ('Bottle', 'Bottle'),
        ('Glass', 'Glass'),
        ('Glass/Bottle', 'Glass/Bottle'),
        ('250ml Bottle', '250ml Bottle'),
        ('250 Gram', '250 Gram'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    unit_type = models.CharField(max_length=50, choices=UNIT_CHOICES, default='KG')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    current_stock = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    minimum_stock_level = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('5.00'))
    expiry_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.unit_type})"

    @property
    def profit_margin(self):
        if self.purchase_price and self.purchase_price > 0:
            return ((self.sale_price - self.purchase_price) / self.purchase_price) * 100
        return Decimal('0')

    @property
    def is_low_stock(self):
        return self.current_stock <= self.minimum_stock_level


class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('Increase', 'Increase'),
        ('Decrease', 'Decrease'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=300)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    adjustment_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.adjustment_type} {self.quantity} {self.product.unit_type} - {self.product.name}"
