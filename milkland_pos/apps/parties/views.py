from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from apps.parties.models import Customer, Supplier
from apps.parties.forms import CustomerForm, SupplierForm


# ---- Customer Views ----

@login_required
def customer_list(request):
    customers = Customer.objects.all()
    query = request.GET.get('q', '')
    pending = request.GET.get('pending', '')
    if query:
        customers = customers.filter(name__icontains=query) | customers.filter(phone__icontains=query)
    if pending:
        customers = customers.filter(current_balance__gt=0)
    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    return render(request, 'parties/customer_list.html', {
        'customers': paginator.get_page(page),
        'query': query,
        'pending': pending,
    })


@login_required
def customer_add(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.current_balance = customer.opening_balance
            customer.save()
            messages.success(request, f'Customer "{customer.name}" added.')
            return redirect('parties:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'parties/customer_form.html', {'form': form, 'title': 'Add Customer'})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated.')
            return redirect('parties:customer_detail', pk=pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'parties/customer_form.html', {'form': form, 'customer': customer, 'title': 'Edit Customer'})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    from apps.sales.models import Sale
    from apps.finance.models import CustomerPayment
    sales = Sale.objects.filter(customer=customer).order_by('-created_at')[:10]
    payments = CustomerPayment.objects.filter(customer=customer).order_by('-created_at')[:10]
    return render(request, 'parties/customer_detail.html', {
        'customer': customer, 'sales': sales, 'payments': payments
    })


@login_required
def customer_ledger(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    from apps.sales.models import Sale
    from apps.finance.models import CustomerPayment

    sales = Sale.objects.filter(customer=customer).order_by('created_at')
    payments = CustomerPayment.objects.filter(customer=customer).order_by('created_at')

    # Build ledger entries
    entries = []
    for sale in sales:
        entries.append({
            'date': sale.sale_date,
            'type': 'Sale',
            'description': f'Invoice #{sale.invoice_number}',
            'debit': sale.balance_amount,
            'credit': 0,
            'obj': sale,
        })
    for payment in payments:
        entries.append({
            'date': payment.payment_date,
            'type': 'Payment',
            'description': f'Payment - {payment.get_payment_method_display()}',
            'debit': 0,
            'credit': payment.amount,
            'obj': payment,
        })
    entries.sort(key=lambda x: x['date'])

    # Running balance
    balance = customer.opening_balance
    for e in entries:
        balance += e['debit'] - e['credit']
        e['balance'] = balance

    return render(request, 'parties/customer_ledger.html', {
        'customer': customer, 'entries': entries
    })


# ---- Supplier Views ----

@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    query = request.GET.get('q', '')
    payable = request.GET.get('payable', '')
    if query:
        suppliers = suppliers.filter(name__icontains=query) | suppliers.filter(phone__icontains=query)
    if payable:
        suppliers = suppliers.filter(current_balance__gt=0)
    paginator = Paginator(suppliers, 20)
    page = request.GET.get('page')
    return render(request, 'parties/supplier_list.html', {
        'suppliers': paginator.get_page(page),
        'query': query,
        'payable': payable,
    })


@login_required
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save(commit=False)
            supplier.current_balance = supplier.opening_balance
            supplier.save()
            messages.success(request, f'Supplier "{supplier.name}" added.')
            return redirect('parties:supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'parties/supplier_form.html', {'form': form, 'title': 'Add Supplier'})


@login_required
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier updated.')
            return redirect('parties:supplier_detail', pk=pk)
    else:
        form = SupplierForm(instance=supplier)
    return render(request, 'parties/supplier_form.html', {'form': form, 'supplier': supplier, 'title': 'Edit Supplier'})


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    from apps.purchases.models import Purchase
    from apps.finance.models import SupplierPayment
    purchases = Purchase.objects.filter(supplier=supplier).order_by('-created_at')[:10]
    payments = SupplierPayment.objects.filter(supplier=supplier).order_by('-created_at')[:10]
    return render(request, 'parties/supplier_detail.html', {
        'supplier': supplier, 'purchases': purchases, 'payments': payments
    })


@login_required
def supplier_ledger(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    from apps.purchases.models import Purchase
    from apps.finance.models import SupplierPayment

    purchases = Purchase.objects.filter(supplier=supplier).order_by('created_at')
    payments = SupplierPayment.objects.filter(supplier=supplier).order_by('created_at')

    entries = []
    for purchase in purchases:
        entries.append({
            'date': purchase.purchase_date,
            'type': 'Purchase',
            'description': f'Invoice #{purchase.invoice_number}',
            'debit': 0,
            'credit': purchase.remaining_amount,
            'obj': purchase,
        })
    for payment in payments:
        entries.append({
            'date': payment.payment_date,
            'type': 'Payment',
            'description': f'Payment - {payment.get_payment_method_display()}',
            'debit': payment.amount,
            'credit': 0,
            'obj': payment,
        })
    entries.sort(key=lambda x: x['date'])

    balance = supplier.opening_balance
    for e in entries:
        balance += e['credit'] - e['debit']
        e['balance'] = balance

    return render(request, 'parties/supplier_ledger.html', {
        'supplier': supplier, 'entries': entries
    })
