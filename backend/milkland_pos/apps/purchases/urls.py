from django.urls import path
from apps.purchases import views

app_name = 'purchases'

urlpatterns = [
    path('', views.purchase_list, name='list'),
    path('add/', views.purchase_add, name='add'),
    path('<int:pk>/', views.purchase_detail, name='detail'),
]
