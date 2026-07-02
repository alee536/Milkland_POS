from django.urls import path
from apps.finance import views

app_name = 'finance'

urlpatterns = [
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.expense_add, name='expense_add'),
    path('expenses/<int:pk>/edit/', views.expense_edit, name='expense_edit'),
    path('payments/customer/', views.customer_payment, name='customer_payment'),
    path('payments/supplier/', views.supplier_payment, name='supplier_payment'),
    path('wastage/', views.wastage_list, name='wastage_list'),
    path('wastage/add/', views.wastage_add, name='wastage_add'),
]
