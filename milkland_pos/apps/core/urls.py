from django.urls import path
from apps.core import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/business/', views.business_settings_view, name='business_settings'),
]
