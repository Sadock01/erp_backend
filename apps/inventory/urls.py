# Routes API pour l'inventaire
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'variants', views.ProductVariantViewSet, basename='variant')

urlpatterns = [
    # Inclusion des routes du router
    path('', include(router.urls)),
    
    # Endpoints de test (sans authentification)
    path('test/', views.test_inventory_endpoint, name='test_inventory'),
]
