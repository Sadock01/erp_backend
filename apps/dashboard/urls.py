from django.urls import path
from . import views

urlpatterns = [
    # Dashboard principal
    path('overview/', views.dashboard_all, name='dashboard_overview'),
    
    # KPIs
    path('kpis/', views.dashboard_kpis, name='dashboard_kpis'),
    
    # Graphiques
    path('sales-chart/', views.dashboard_sales_chart, name='dashboard_sales_chart'),
    path('top-products/', views.dashboard_products_chart, name='dashboard_top_products'),
    path('clients-distribution/', views.dashboard_clients_chart, name='dashboard_clients_distribution'),
    
    # Alertes
    path('alerts/', views.dashboard_alerts, name='dashboard_alerts'),
    
    # Données récentes
    path('recent-orders/', views.dashboard_recent_orders, name='dashboard_recent_orders'),
    path('recent-invoices/', views.dashboard_recent_invoices, name='dashboard_recent_invoices'),
]
