import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from apps.purchases.models import Purchase, PurchaseItem
from apps.parties.models import Supplier
from apps.products.models import Product


def generate_purchase_invoice():
    from django.db.models import Max
    last = Purchase.objects.aggregate(Max('id'))['id__max'] or 0
    return f"PUR-{str(last + 1).zfill(5)}"


@login_required
def purchase_list(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    purchases = Purchase.objects.select_related('supplier', 'created_by').all()
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    if query:
        purchases = purchases.filter(supplier__name__icontains=query) | purchases.filter(invoice_number__icontains=query)
    if status:
        purchases = purchases.filter(payment_status=status)

    paginator = Paginator(purchases, 20)
    return render(request, 'purchases/purchase_list.html', {
        'purchases': paginator.get_page(request.GET.get('page')),
        'query': query,
        'status': status,
    })


@login_required
def purchase_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')

    suppliers = Supplier.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True).select_related('category')

    if request.method == 'POST':
        supplier_id = request.POST.get('supplier')
        purchase_date = request.POST.get('purchase_date')
        paid_amount = Decimal(request.POST.get('paid_amount', '0') or '0')
        notes = request.POST.get('notes', '')
        items_json = request.POST.get('items_data', '[]')

        try:
            items = json.loads(items_json)
        except Exception:
            items = []

        if not items:
            messages.error(request, 'Purchase must have at least one item.')
            return render(request, 'purchases/purchase_form.html', {'suppliers': suppliers, 'products': products})

        try:
            supplier = Supplier.objects.get(pk=supplier_id)
        except Supplier.DoesNotExist:
            messages.error(request, 'Invalid supplier.')
            return render(request, 'purchases/purchase_form.html', {'suppliers': suppliers, 'products': products})

        with transaction.atomic():
            invoice_number = generate_purchase_invoice()
            total_amount = sum(Decimal(str(i['qty'])) * Decimal(str(i['rate'])) for i in items)

            if paid_amount < 0:
                messages.error(request, 'Paid amount cannot be negative.')
                return render(request, 'purchases/purchase_form.html', {'suppliers': suppliers, 'products': products})
            if paid_amount > total_amount:
                paid_amount = total_amount

            purchase = Purchase.objects.create(
                invoice_number=invoice_number,
                supplier=supplier,
                purchase_date=purchase_date,
                total_amount=total_amount,
                paid_amount=paid_amount,
                created_by=request.user,
                notes=notes,
            )

            for item in items:
                product = Product.objects.select_for_update().get(pk=item['product_id'])
                qty = Decimal(str(item['qty']))
                rate = Decimal(str(item['rate']))
                PurchaseItem.objects.create(
                    purchase=purchase,
                    product=product,
                    quantity=qty,
                    purchase_rate=rate,
                    line_total=qty * rate,
                )
                product.current_stock += qty
                product.save()

            remaining = total_amount - paid_amount
            if remaining > 0:
                supplier.current_balance += remaining
                supplier.save()

        messages.success(request, f'Purchase #{invoice_number} saved successfully.')
        return redirect('purchases:detail', pk=purchase.pk)

    return render(request, 'purchases/purchase_form.html', {
        'suppliers': suppliers,
        'products': products,
        'today': timezone.localdate(),
    })


@login_required
def purchase_detail(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('core:dashboard')
    purchase = get_object_or_404(Purchase, pk=pk)
    items = purchase.items.select_related('product').all()
    return render(request, 'purchases/purchase_detail.html', {'purchase': purchase, 'items': items})
