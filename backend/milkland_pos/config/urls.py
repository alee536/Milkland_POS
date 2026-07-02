from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls', namespace='accounts')),
    path('', include('apps.core.urls', namespace='core')),
    path('products/', include('apps.products.urls', namespace='products')),
    path('', include('apps.parties.urls', namespace='parties')),
    path('purchases/', include('apps.purchases.urls', namespace='purchases')),
    path('sales/', include('apps.sales.urls', namespace='sales')),
    path('', include('apps.finance.urls', namespace='finance')),
    path('reports/', include('apps.reports.urls', namespace='reports')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
