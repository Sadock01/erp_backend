from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='orderitem')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')
router.register(r'proformas', views.ProformaInvoiceViewSet, basename='proformainvoice')
router.register(r'payments', views.PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', views.test_sales_endpoint, name='test_sales'),
    
    # APIs de résumé pour le dashboard
    path('orders/summary/', views.orders_summary, name='orders_summary'),
    path('invoices/summary/', views.invoices_summary, name='invoices_summary'),
]