import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from decimal import Decimal
from apps.sales.models import Sale, SaleItem
from apps.parties.models import Customer
from apps.products.models import Product


def generate_sale_invoice():
    from django.db.models import Max
    last = Sale.objects.aggregate(Max('id'))['id__max'] or 0
    return f"SL-{str(last + 1).zfill(5)}"


@login_required
def pos(request):
    products = Product.objects.filter(is_active=True).select_related('category').order_by('category__name', 'name')
    customers = Customer.objects.filter(is_active=True).order_by('name')
    categories = set(p.category for p in products if p.category)

    if request.method == 'POST':
        customer_id = request.POST.get('customer_id', '')
        sale_type = request.POST.get('sale_type', 'Cash')
        discount_pct = Decimal(request.POST.get('discount_percentage', '0') or '0')
        paid_amount = Decimal(request.POST.get('paid_amount', '0') or '0')
        notes = request.POST.get('notes', '')
        items_json = request.POST.get('items_data', '[]')

        try:
            items = json.loads(items_json)
        except Exception:
            items = []

        if not items:
            messages.error(request, 'Cart is empty. Please add at least one product.')
            return render(request, 'sales/pos.html', {'products': products, 'customers': customers, 'categories': categories})

        if sale_type == 'Credit' and not customer_id:
            messages.error(request, 'Credit sale requires a customer.')
            return render(request, 'sales/pos.html', {'products': products, 'customers': customers, 'categories': categories})

        customer = None
        if customer_id:
            try:
                customer = Customer.objects.get(pk=customer_id)
            except Customer.DoesNotExist:
                pass

        with transaction.atomic():
            invoice_number = generate_sale_invoice()
            total_amount = sum(Decimal(str(i['qty'])) * Decimal(str(i['rate'])) for i in items)
            discount_amount = total_amount * discount_pct / Decimal('100')
            grand_total = total_amount - discount_amount
            balance_amount = max(grand_total - paid_amount, Decimal('0'))

            sale = Sale.objects.create(
                invoice_number=invoice_number,
                customer=customer,
                sale_date=timezone.localdate(),
                sale_type=sale_type,
                total_amount=total_amount,
                discount_percentage=discount_pct,
                discount_amount=discount_amount,
                grand_total=grand_total,
                paid_amount=paid_amount,
                balance_amount=balance_amount,
                cashier=request.user,
                notes=notes,
            )

            for item in items:
                product = Product.objects.select_for_update().get(pk=item['product_id'])
                qty = Decimal(str(item['qty']))
                if product.current_stock < qty:
                    raise ValueError(f"Insufficient stock for {product.name}. Available: {product.current_stock} {product.unit_type}")
                rate = Decimal(str(item['rate']))
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    sale_rate=rate,
                    line_total=qty * rate,
                )
                product.current_stock -= qty
                product.save()

            if sale_type == 'Credit' and customer:
                customer.current_balance += balance_amount
                customer.save()
            elif sale_type == 'Cash' and customer and balance_amount > 0:
                customer.current_balance += balance_amount
                customer.save()

        messages.success(request, f'Sale #{invoice_number} completed successfully!')
        return redirect('sales:receipt', pk=sale.pk)

    return render(request, 'sales/pos.html', {
        'products': products,
        'customers': customers,
        'categories': list(categories),
    })


@login_required
def sale_list(request):
    sales = Sale.objects.select_related('customer', 'cashier').all()
    query = request.GET.get('q', '')
    sale_type = request.GET.get('sale_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if query:
        sales = sales.filter(invoice_number__icontains=query)
    if sale_type:
        sales = sales.filter(sale_type=sale_type)
    if date_from:
        sales = sales.filter(sale_date__gte=date_from)
    if date_to:
        sales = sales.filter(sale_date__lte=date_to)

    paginator = Paginator(sales, 20)
    return render(request, 'sales/sale_list.html', {
        'sales': paginator.get_page(request.GET.get('page')),
        'query': query, 'sale_type': sale_type,
        'date_from': date_from, 'date_to': date_to,
    })


@login_required
def sale_detail(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.select_related('product').all()
    return render(request, 'sales/sale_detail.html', {'sale': sale, 'items': items})


@login_required
def sale_receipt(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    items = sale.items.select_related('product').all()
    return render(request, 'sales/receipt.html', {'sale': sale, 'items': items})


@login_required
def get_product_info(request, pk):
    try:
        p = Product.objects.get(pk=pk, is_active=True)
        return JsonResponse({
            'id': p.pk,
            'name': p.name,
            'sale_price': str(p.sale_price),
            'current_stock': str(p.current_stock),
            'unit_type': p.unit_type,
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)
