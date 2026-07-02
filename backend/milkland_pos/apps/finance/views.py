from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from decimal import Decimal
from apps.finance.models import CustomerPayment, SupplierPayment, Expense, Wastage, ExpenseCategory
from apps.finance.forms import CustomerPaymentForm, SupplierPaymentForm, ExpenseForm, WastageForm
from apps.parties.models import Customer, Supplier


@login_required
def expense_list(request):
    expenses = Expense.objects.select_related('category', 'added_by').all()
    query = request.GET.get('q', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    if query:
        expenses = expenses.filter(description__icontains=query)
    if date_from:
        expenses = expenses.filter(expense_date__gte=date_from)
    if date_to:
        expenses = expenses.filter(expense_date__lte=date_to)
    paginator = Paginator(expenses, 20)
    return render(request, 'finance/expense_list.html', {
        'expenses': paginator.get_page(request.GET.get('page')),
        'query': query, 'date_from': date_from, 'date_to': date_to,
    })


@login_required
def expense_add(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.added_by = request.user
            expense.save()
            messages.success(request, 'Expense recorded.')
            return redirect('finance:expense_list')
    else:
        form = ExpenseForm(initial={'expense_date': timezone.localdate()})
    return render(request, 'finance/expense_form.html', {'form': form, 'title': 'Add Expense'})


@login_required
def expense_edit(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated.')
            return redirect('finance:expense_list')
    else:
        form = ExpenseForm(instance=expense)
    return render(request, 'finance/expense_form.html', {'form': form, 'expense': expense, 'title': 'Edit Expense'})


@login_required
def customer_payment(request):
    customer_id = request.GET.get('customer', '')
    initial = {'payment_date': timezone.localdate()}
    if customer_id:
        try:
            c = Customer.objects.get(pk=customer_id)
            initial['customer'] = c
        except Customer.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CustomerPaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payment = form.save(commit=False)
                payment.received_by = request.user
                customer = payment.customer
                if payment.amount <= 0:
                    messages.error(request, 'Payment amount must be positive.')
                    return render(request, 'finance/customer_payment_form.html', {'form': form})
                customer.current_balance -= payment.amount
                customer.save()
                payment.save()
            messages.success(request, f'Payment of PKR {payment.amount} received from {payment.customer.name}.')
            return redirect('parties:customer_ledger', pk=payment.customer.pk)
    else:
        form = CustomerPaymentForm(initial=initial)
    return render(request, 'finance/customer_payment_form.html', {'form': form})


@login_required
def supplier_payment(request):
    supplier_id = request.GET.get('supplier', '')
    initial = {'payment_date': timezone.localdate()}
    if supplier_id:
        try:
            s = Supplier.objects.get(pk=supplier_id)
            initial['supplier'] = s
        except Supplier.DoesNotExist:
            pass

    if request.method == 'POST':
        form = SupplierPaymentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                payment = form.save(commit=False)
                payment.paid_by = request.user
                supplier = payment.supplier
                if payment.amount <= 0:
                    messages.error(request, 'Payment amount must be positive.')
                    return render(request, 'finance/supplier_payment_form.html', {'form': form})
                supplier.current_balance -= payment.amount
                supplier.save()
                payment.save()
            messages.success(request, f'Payment of PKR {payment.amount} made to {payment.supplier.name}.')
            return redirect('parties:supplier_ledger', pk=payment.supplier.pk)
    else:
        form = SupplierPaymentForm(initial=initial)
    return render(request, 'finance/supplier_payment_form.html', {'form': form})


@login_required
def wastage_list(request):
    wastages = Wastage.objects.select_related('product', 'added_by').all()
    paginator = Paginator(wastages, 20)
    return render(request, 'finance/wastage_list.html', {
        'wastages': paginator.get_page(request.GET.get('page'))
    })


@login_required
def wastage_add(request):
    if request.method == 'POST':
        form = WastageForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                wastage = form.save(commit=False)
                wastage.added_by = request.user
                product = wastage.product
                if product.current_stock < wastage.quantity:
                    messages.error(request, f'Cannot waste more than current stock ({product.current_stock} {product.unit_type}).')
                    return render(request, 'finance/wastage_form.html', {'form': form})
                wastage.estimated_loss_amount = product.purchase_price * wastage.quantity
                product.current_stock -= wastage.quantity
                product.save()
                wastage.save()
            messages.success(request, 'Wastage recorded successfully.')
            return redirect('finance:wastage_list')
    else:
        form = WastageForm(initial={'wastage_date': timezone.localdate()})
    return render(request, 'finance/wastage_form.html', {'form': form})
