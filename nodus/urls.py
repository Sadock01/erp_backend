"""
URL configuration for nodus project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Authentification
    path('api/', include('apps.common.urls')),
    
    # Dashboard
    path('api/dashboard/', include('apps.dashboard.urls')),
    
    # API URLs
    path('api/customers/', include('apps.customers.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/stock/', include('apps.stock.urls')),
    path('api/sales/', include('apps.sales.urls')),
    path('api/permissions/', include('apps.permissions.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
