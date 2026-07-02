from django.urls import path
from apps.sales import views

app_name = 'sales'

urlpatterns = [
    path('pos/', views.pos, name='pos'),
    path('', views.sale_list, name='list'),
    path('<int:pk>/', views.sale_detail, name='detail'),
    path('<int:pk>/receipt/', views.sale_receipt, name='receipt'),
    path('api/product/<int:pk>/', views.get_product_info, name='product_info'),
]
