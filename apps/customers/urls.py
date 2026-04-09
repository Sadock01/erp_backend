# Routes API pour les clients
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'', views.CustomerViewSet, basename='customer')

urlpatterns = [
    # Endpoint de test (sans authentification) - AVANT les routes du ViewSet
    path('test/', views.test_endpoint, name='test'),
    
    # Analytics endpoints
    path('analytics/kpis/', views.customers_analytics_kpis, name='customers_analytics_kpis'),
    
    # Inclusion des routes du router - APRÈS les routes spécifiques
    path('', include(router.urls)),
]
