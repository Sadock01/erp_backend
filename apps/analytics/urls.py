from django.urls import path
from . import views

urlpatterns = [
    # Endpoint principal - Données complètes
    path('', views.analytics_main, name='analytics_main'),
    
    # Endpoints spécifiques
    path('kpis/', views.analytics_kpis, name='analytics_kpis'),
    path('revenue-chart/', views.analytics_revenue_chart, name='analytics_revenue_chart'),
    path('sales-performance/', views.analytics_sales_performance, name='analytics_sales_performance'),
    path('top-customers/', views.analytics_top_customers, name='analytics_top_customers'),
    path('top-products/', views.analytics_top_products, name='analytics_top_products'),
]
