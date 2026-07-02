from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from django.utils import timezone
from apps.products.models import Product, Category, StockAdjustment
from apps.products.forms import ProductForm, CategoryForm, StockAdjustmentForm


@login_required
def product_list(request):
    products = Product.objects.select_related('category').all()
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    low_stock = request.GET.get('low_stock', '')
    status = request.GET.get('status', '')

    if query:
        products = products.filter(name__icontains=query)
    if category_id:
        products = products.filter(category_id=category_id)
    if low_stock:
        products = [p for p in products if p.is_low_stock]
    if status == 'active':
        products = products.filter(is_active=True) if not low_stock else [p for p in products if p.is_active]
    elif status == 'inactive':
        products = products.filter(is_active=False) if not low_stock else [p for p in products if not p.is_active]

    if not isinstance(products, list):
        paginator = Paginator(products, 20)
    else:
        paginator = Paginator(products, 20)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    categories = Category.objects.filter(is_active=True)
    context = {
        'products': products_page,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'low_stock': low_stock,
        'status': status,
    }
    return render(request, 'products/product_list.html', context)


@login_required
def product_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('products:list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.updated_by = request.user
            product.save()
            messages.success(request, f'Product "{product.name}" added successfully.')
            return redirect('products:list')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('products:list')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            p = form.save(commit=False)
            p.updated_by = request.user
            p.save()
            messages.success(request, f'Product "{p.name}" updated successfully.')
            return redirect('products:detail', pk=p.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {'form': form, 'product': product, 'title': 'Edit Product'})


@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    adjustments = StockAdjustment.objects.filter(product=product).order_by('-created_at')[:10]
    from apps.sales.models import SaleItem
    recent_sales = SaleItem.objects.filter(product=product).select_related('sale').order_by('-sale__created_at')[:10]
    context = {
        'product': product,
        'adjustments': adjustments,
        'recent_sales': recent_sales,
    }
    return render(request, 'products/product_detail.html', context)


@login_required
def product_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('products:list')

    product = get_object_or_404(Product, pk=pk)

    from apps.sales.models import SaleItem
    from apps.purchases.models import PurchaseItem
    if SaleItem.objects.filter(product=product).exists() or PurchaseItem.objects.filter(product=product).exists():
        messages.error(request, f'Cannot delete "{product.name}" - it has sales/purchase history.')
        return redirect('products:detail', pk=pk)

    name = product.name
    product.delete()
    messages.success(request, f'Product "{name}" deleted successfully.')
    return redirect('products:list')


@login_required
def stock_adjust(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Only admin can adjust stock manually.')
        return redirect('products:detail', pk=pk)

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                adj = form.save(commit=False)
                adj.product = product
                adj.adjusted_by = request.user
                qty = adj.quantity
                if adj.adjustment_type == 'Increase':
                    product.current_stock += qty
                else:
                    if product.current_stock < qty:
                        messages.error(request, 'Cannot decrease stock below zero.')
                        return render(request, 'products/stock_adjust.html', {'form': form, 'product': product})
                    product.current_stock -= qty
                product.save()
                adj.save()
                messages.success(request, f'Stock adjusted: {adj.adjustment_type} {qty} {product.unit_type}.')
                return redirect('products:detail', pk=pk)
    else:
        form = StockAdjustmentForm(initial={'adjustment_date': timezone.localdate()})

    return render(request, 'products/stock_adjust.html', {'form': form, 'product': product})


@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})


@login_required
def category_add(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('products:category_list')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save()
            messages.success(request, f'Category "{cat.name}" added.')
            return redirect('products:category_list')
    else:
        form = CategoryForm()
    return render(request, 'products/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('products:category_list')

    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated.')
            return redirect('products:category_list')
    else:
        form = CategoryForm(instance=cat)
    return render(request, 'products/category_form.html', {'form': form, 'category': cat, 'title': 'Edit Category'})
