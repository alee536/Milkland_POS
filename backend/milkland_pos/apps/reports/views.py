import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from decimal import Decimal
from apps.sales.models import Sale, SaleItem
from apps.purchases.models import Purchase
from apps.finance.models import Expense, Wastage
from apps.products.models import Product
from apps.parties.models import Customer, Supplier


@login_required
def reports_dashboard(request):
    return render(request, 'reports/reports_dashboard.html')


@login_required
def sales_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sale_type = request.GET.get('sale_type', '')

    sales = Sale.objects.select_related('customer', 'cashier').all()
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)
    if sale_type:
        sales = sales.filter(sale_type=sale_type)

    totals = sales.aggregate(
        total_sales=Sum('grand_total'),
        total_paid=Sum('paid_amount'),
        total_balance=Sum('balance_amount'),
        count=Count('id'),
    )

    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Invoice', 'Date', 'Customer', 'Type', 'Total', 'Paid', 'Balance'])
        for s in sales:
            writer.writerow([s.invoice_number, s.sale_date, s.customer or 'Walk-in', s.sale_type,
                              s.grand_total, s.paid_amount, s.balance_amount])
        return response

    return render(request, 'reports/sales_report.html', {
        'sales': sales, 'totals': totals,
        'date_from': date_from, 'date_to': date_to, 'sale_type': sale_type,
    })


@login_required
def stock_report(request):
    products = Product.objects.select_related('category').filter(is_active=True).order_by('category__name', 'name')
    low_stock_only = request.GET.get('low_stock', '')
    if low_stock_only:
        products = [p for p in products if p.is_low_stock]
    total_value = sum(p.current_stock * p.purchase_price for p in products)
    return render(request, 'reports/stock_report.html', {
        'products': products, 'total_value': total_value, 'low_stock_only': low_stock_only
    })


@login_required
def customer_credit_report(request):
    customers = Customer.objects.filter(current_balance__gt=0).order_by('-current_balance')
    total = customers.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    return render(request, 'reports/customer_credit_report.html', {
        'customers': customers, 'total': total
    })


@login_required
def supplier_payable_report(request):
    suppliers = Supplier.objects.filter(current_balance__gt=0).order_by('-current_balance')
    total = suppliers.aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    return render(request, 'reports/supplier_payable_report.html', {
        'suppliers': suppliers, 'total': total
    })


@login_required
def expense_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    expenses = Expense.objects.select_related('category', 'added_by').all()
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)
    total = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    return render(request, 'reports/expense_report.html', {
        'expenses': expenses, 'total': total,
        'date_from': date_from, 'date_to': date_to,
    })


@login_required
def wastage_report(request):
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    wastages = Wastage.objects.select_related('product', 'added_by').all()
    if date_from:
        wastages = wastages.filter(wastage_date__gte=date_from)
    if date_to:
        wastages = wastages.filter(wastage_date__lte=date_to)
    total_loss = wastages.aggregate(total=Sum('estimated_loss_amount'))['total'] or Decimal('0')
    return render(request, 'reports/wastage_report.html', {
        'wastages': wastages, 'total_loss': total_loss,
        'date_from': date_from, 'date_to': date_to,
    })


@login_required
def profit_loss_report(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        from django.shortcuts import redirect
        return redirect('reports:dashboard')

    date_from = request.GET.get('date_from', str(timezone.localdate().replace(day=1)))
    date_to = request.GET.get('date_to', str(timezone.localdate()))

    sales = Sale.objects.filter(sale_date__gte=date_from, sale_date__lte=date_to)
    total_revenue = sales.aggregate(total=Sum('grand_total'))['total'] or Decimal('0')

    sale_items = SaleItem.objects.filter(sale__in=sales)
    cogs = sum(item.quantity * item.product.purchase_price for item in sale_items)

    expenses = Expense.objects.filter(expense_date__gte=date_from, expense_date__lte=date_to)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0')

    wastages = Wastage.objects.filter(wastage_date__gte=date_from, wastage_date__lte=date_to)
    total_wastage_loss = wastages.aggregate(total=Sum('estimated_loss_amount'))['total'] or Decimal('0')

    gross_profit = total_revenue - Decimal(str(cogs))
    net_profit = gross_profit - total_expenses - total_wastage_loss

    return render(request, 'reports/profit_loss_report.html', {
        'date_from': date_from, 'date_to': date_to,
        'total_revenue': total_revenue,
        'cogs': Decimal(str(cogs)),
        'gross_profit': gross_profit,
        'total_expenses': total_expenses,
        'total_wastage_loss': total_wastage_loss,
        'net_profit': net_profit,
        'sales_count': sales.count(),
    })
