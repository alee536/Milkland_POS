from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count, Q
from decimal import Decimal
import json
from apps.core.models import BusinessSettings
from apps.products.models import Product
from apps.sales.models import Sale, SaleItem
from apps.purchases.models import Purchase
from apps.finance.models import Expense, CustomerPayment
from apps.parties.models import Customer, Supplier


@login_required
def dashboard(request):
    today = timezone.localdate()

    today_sales = Sale.objects.filter(sale_date=today)
    today_sales_total = today_sales.aggregate(total=Sum('grand_total'))['total'] or Decimal('0')
    today_cash_sales = today_sales.filter(sale_type='Cash').aggregate(total=Sum('grand_total'))['total'] or Decimal('0')
    today_credit_sales = today_sales.filter(sale_type='Credit').aggregate(total=Sum('grand_total'))['total'] or Decimal('0')
    today_orders_count = today_sales.count()

    today_expenses = Expense.objects.filter(expense_date=today)
    today_expenses_total = today_expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    today_sale_ids = today_sales.values_list('id', flat=True)
    today_items = SaleItem.objects.filter(sale_id__in=today_sale_ids)
    today_revenue = today_items.aggregate(total=Sum('line_total'))['total'] or Decimal('0')
    today_cogs = sum(
        item.quantity * (item.product.purchase_price or Decimal('0'))
        for item in today_items
    )
    today_profit = today_revenue - Decimal(str(today_cogs)) - today_expenses_total

    total_stock_value = sum(
        p.current_stock * p.purchase_price
        for p in Product.objects.filter(is_active=True)
    )

    customer_receivable = Customer.objects.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    total_supplier_payable = Supplier.objects.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')

    low_stock_count = Product.objects.filter(
        is_active=True,
        current_stock__lte=models_low_stock_threshold()
    ).count()

    # 7-day chart data
    chart_labels = []
    chart_sales = []
    chart_profit = []
    for i in range(6, -1, -1):
        day = today - timezone.timedelta(days=i)
        day_sales = Sale.objects.filter(sale_date=day)
        day_total = day_sales.aggregate(t=Sum('grand_total'))['t'] or Decimal('0')
        day_ids = day_sales.values_list('id', flat=True)
        day_items = SaleItem.objects.filter(sale_id__in=day_ids)
        day_rev = day_items.aggregate(t=Sum('line_total'))['t'] or Decimal('0')
        day_cogs = sum(
            it.quantity * (it.product.purchase_price or Decimal('0'))
            for it in day_items
        )
        day_exp = Expense.objects.filter(expense_date=day).aggregate(t=Sum('amount'))['t'] or Decimal('0')
        day_profit = day_rev - Decimal(str(day_cogs)) - day_exp

        chart_labels.append(day.strftime('%b %d'))
        chart_sales.append(float(day_total))
        chart_profit.append(float(max(day_profit, Decimal('0'))))

    # Top products (last 7 days)
    week_start = today - timezone.timedelta(days=6)
    top_products = list(
        SaleItem.objects
        .filter(sale__sale_date__gte=week_start)
        .values('product__name')
        .annotate(qty=Sum('quantity'), revenue=Sum('line_total'))
        .order_by('-revenue')[:5]
    )

    context = {
        'today_sales_total': today_sales_total,
        'today_cash_sales': today_cash_sales,
        'today_credit_sales': today_credit_sales,
        'today_orders_count': today_orders_count,
        'today_expenses_total': today_expenses_total,
        'today_profit': today_profit,
        'total_stock_value': total_stock_value,
        'customer_receivable': customer_receivable,
        'total_supplier_payable': total_supplier_payable,
        'low_stock_count': low_stock_count,
        'chart_labels': json.dumps(chart_labels),
        'chart_sales': json.dumps(chart_sales),
        'chart_profit': json.dumps(chart_profit),
        'top_products': top_products,
    }
    return render(request, 'dashboard.html', context)


def models_low_stock_threshold():
    return 5


@login_required
def business_settings_view(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    settings = BusinessSettings.get_settings()

    if request.method == 'POST':
        settings.shop_name = request.POST.get('shop_name', settings.shop_name)
        settings.tagline = request.POST.get('tagline', settings.tagline)
        settings.service_highlight = request.POST.get('service_highlight', settings.service_highlight)
        settings.address = request.POST.get('address', settings.address)
        settings.contact_number = request.POST.get('contact_number', settings.contact_number)
        settings.receipt_footer_message = request.POST.get('receipt_footer_message', settings.receipt_footer_message)
        settings.currency_symbol = request.POST.get('currency_symbol', settings.currency_symbol)
        settings.low_stock_alert_enabled = 'low_stock_alert_enabled' in request.POST
        if 'receipt_logo' in request.FILES:
            settings.receipt_logo = request.FILES['receipt_logo']
        settings.save()
        messages.success(request, 'Business settings updated successfully.')
        return redirect('core:business_settings')

    return render(request, 'settings/business_settings.html', {'settings': settings})
