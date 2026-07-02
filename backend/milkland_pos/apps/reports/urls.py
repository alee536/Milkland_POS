from django.urls import path
from apps.reports import views

app_name = 'reports'

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard'),
    path('sales/', views.sales_report, name='sales'),
    path('stock/', views.stock_report, name='stock'),
    path('customer-credit/', views.customer_credit_report, name='customer_credit'),
    path('supplier-payable/', views.supplier_payable_report, name='supplier_payable'),
    path('expenses/', views.expense_report, name='expenses'),
    path('wastage/', views.wastage_report, name='wastage'),
    path('profit-loss/', views.profit_loss_report, name='profit_loss'),
]
