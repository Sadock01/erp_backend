from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'movements', views.StockMovementViewSet, basename='stockmovement')
router.register(r'adjustments', views.StockAdjustmentViewSet, basename='stockadjustment')
router.register(r'alerts', views.StockAlertViewSet, basename='stockalert')
router.register(r'reports', views.StockReportViewSet, basename='stockreport')

urlpatterns = [
    path('', include(router.urls)),
    path('test/', views.test_stock_endpoint, name='test_stock'),
    
    # API de résumé pour le dashboard
    path('movements/summary/', views.movements_summary, name='movements_summary'),
]