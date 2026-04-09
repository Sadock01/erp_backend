from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, F

from .models import Category, Product, ProductVariant, ProductImage
from .serializers import (
    CategorySerializer,
    CategoryListSerializer,
    ProductSerializer,
    ProductListSerializer,
    ProductCreateSerializer,
    ProductVariantSerializer,
    ProductVariantCreateSerializer,
    ProductImageSerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des catégories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtres
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'sort_order', 'created_at']
    ordering = ['sort_order', 'name']

    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retourne uniquement les catégories actives"""
        active_categories = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Retourne les produits de cette catégorie"""
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des produits
    """
    queryset = Product.objects.select_related('category').prefetch_related('variants', 'images')
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtres
    filterset_fields = ['status', 'product_type', 'category', 'is_digital', 'is_featured']
    search_fields = ['name', 'description', 'sku', 'barcode', 'tags']
    ordering_fields = ['name', 'price', 'created_at', 'updated_at']
    ordering = ['name']

    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        return ProductSerializer

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retourne uniquement les produits actifs"""
        active_products = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Retourne les produits vedettes"""
        featured_products = self.get_queryset().filter(is_featured=True, status='active')
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Retourne les variants d'un produit"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche avancée de produits"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Paramètre de recherche requis'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        products = self.get_queryset().filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(sku__icontains=query) |
            Q(barcode__icontains=query) |
            Q(tags__icontains=query)
        )
        
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des variants de produits
    """
    queryset = ProductVariant.objects.select_related('product')
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtres
    filterset_fields = ['product', 'variant_type', 'is_active']
    search_fields = ['name', 'sku', 'value']
    ordering_fields = ['name', 'sort_order', 'stock_quantity']
    ordering = ['product', 'sort_order', 'name']

    def get_serializer_class(self):
        """Retourne le serializer approprié selon l'action"""
        if self.action == 'create':
            return ProductVariantCreateSerializer
        return ProductVariantSerializer


# Endpoints de test (sans authentification)
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_inventory_endpoint(request):
    """Endpoint de test pour l'inventaire"""
    if request.method == 'GET':
        return Response({
            'message': 'API Inventory fonctionne !',
            'method': 'GET',
            'status': 'success'
        })
    elif request.method == 'POST':
        return Response({
            'message': 'API Inventory fonctionne !',
            'method': 'POST',
            'data_received': request.data,
            'status': 'success'
        })
