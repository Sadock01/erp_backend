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
    ProductUpdateSerializer,
    ProductVariantSerializer,
    ProductVariantCreateSerializer,
    ProductImageSerializer,
    ProductWithVariantsCreateSerializer
)
from apps.permissions.decorators import user_has_permission
from apps.common.mixins import CompanyFilterMixin


class CategoryViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des catégories - SÉCURISÉ
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

    def list(self, request, *args, **kwargs):
        """Lister les catégories - Nécessite inventory_category.view"""
        if not user_has_permission(request.user, 'inventory_category.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les catégories',
                'required_permission': 'inventory_category.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer une catégorie - Nécessite inventory_category.create"""
        if not user_has_permission(request.user, 'inventory_category.create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des catégories',
                'required_permission': 'inventory_category.create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir une catégorie - Nécessite inventory_category.view"""
        if not user_has_permission(request.user, 'inventory_category.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les catégories',
                'required_permission': 'inventory_category.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier une catégorie - Nécessite inventory_category.update"""
        if not user_has_permission(request.user, 'inventory_category.update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les catégories',
                'required_permission': 'inventory_category.update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer une catégorie - Nécessite inventory_category.delete"""
        if not user_has_permission(request.user, 'inventory_category.delete'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les catégories',
                'required_permission': 'inventory_category.delete'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retourne uniquement les catégories actives - Nécessite inventory_category.view"""
        if not user_has_permission(request.user, 'inventory_category.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les catégories',
                'required_permission': 'inventory_category.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_categories = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Retourne les produits de cette catégorie - Nécessite inventory_category.view"""
        if not user_has_permission(request.user, 'inventory_category.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les catégories',
                'required_permission': 'inventory_category.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        category = self.get_object()
        products = Product.objects.filter(category=category)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des produits - SÉCURISÉ
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
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductSerializer

    def list(self, request, *args, **kwargs):
        """Lister les produits - Nécessite inventory_view"""
        if not user_has_permission(request.user, 'inventory_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les produits',
                'required_permission': 'inventory_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Retourner simplement les produits (sans mélanger avec les variants)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un produit - Nécessite inventory_create"""
        if not user_has_permission(request.user, 'inventory_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des produits',
                'required_permission': 'inventory_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['post'], url_path='with-variants')
    def create_with_variants(self, request):
        """Créer un produit avec ses variants en une seule requête"""
        if not user_has_permission(request.user, 'inventory_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des produits',
                'required_permission': 'inventory_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductWithVariantsCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            product = serializer.save()
            
            # Retourner le produit avec ses variants
            response_serializer = ProductSerializer(product, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        """Voir un produit - Nécessite inventory_view"""
        if not user_has_permission(request.user, 'inventory_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les produits',
                'required_permission': 'inventory_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un produit - Nécessite inventory_update"""
        if not user_has_permission(request.user, 'inventory_update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les produits',
                'required_permission': 'inventory_update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def get_serializer_context(self):
        """Ajouter le produit au contexte pour la validation des images"""
        context = super().get_serializer_context()
        if self.action in ['update', 'partial_update'] and 'pk' in self.kwargs:
            try:
                product = self.get_object()
                context['product'] = product
            except:
                pass
        return context

    def destroy(self, request, *args, **kwargs):
        """Supprimer un produit - Nécessite inventory_delete"""
        if not user_has_permission(request.user, 'inventory_delete'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les produits',
                'required_permission': 'inventory_delete'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Vérifier si l'ID correspond à un variant
            from apps.inventory.models import ProductVariant
            variant_id = kwargs.get('pk')
            
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                # Si c'est un variant, le supprimer
                variant.delete()
                return Response({
                    'message': 'Variant supprimé avec succès',
                    'variant_id': variant_id
                }, status=status.HTTP_200_OK)
            except ProductVariant.DoesNotExist:
                # Si ce n'est pas un variant, essayer de supprimer comme un produit
                return super().destroy(request, *args, **kwargs)
                
        except Exception as e:
            # Vérifier si c'est une erreur de contrainte de clé étrangère
            if 'ProtectedError' in str(type(e)) or 'protected foreign keys' in str(e):
                return Response({
                    'error': 'Impossible de supprimer',
                    'detail': 'Ce produit ne peut pas être supprimé car il est utilisé dans des commandes. Vous pouvez le désactiver à la place.',
                    'suggestion': 'Utilisez PATCH pour marquer le produit comme inactif'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                    'error': 'Erreur de suppression',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactiver un produit - Nécessite inventory_update"""
        if not user_has_permission(request.user, 'inventory_update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les produits',
                'required_permission': 'inventory_update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        product = self.get_object()
        product.is_active = False
        product.save()
        
        serializer = self.get_serializer(product)
        return Response({
            'message': 'Produit désactivé avec succès',
            'product': serializer.data
        })

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer un produit - Nécessite inventory_update"""
        if not user_has_permission(request.user, 'inventory_update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les produits',
                'required_permission': 'inventory_update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        product = self.get_object()
        product.is_active = True
        product.save()
        
        serializer = self.get_serializer(product)
        return Response({
            'message': 'Produit activé avec succès',
            'product': serializer.data
        })

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Retourne uniquement les produits actifs - Nécessite inventory_view"""
        if not user_has_permission(request.user, 'inventory_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les produits',
                'required_permission': 'inventory_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_products = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(active_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Retourne les produits vedettes - Nécessite inventory_view"""
        if not user_has_permission(request.user, 'inventory_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les produits',
                'required_permission': 'inventory_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        featured_products = self.get_queryset().filter(is_featured=True, status='active')
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Retourne les variants d'un produit - Nécessite inventory_view"""
        if not user_has_permission(request.user, 'inventory_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les produits',
                'required_permission': 'inventory_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        product = self.get_object()
        variants = product.variants.all()
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Recherche avancée de produits - Nécessite inventory_view"""
        if not user_has_permission(request.user, 'inventory_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les produits',
                'required_permission': 'inventory_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
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
    ViewSet pour la gestion des variants de produits - SÉCURISÉ
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

    def list(self, request, *args, **kwargs):
        """Lister les variants - Nécessite inventory_variant.view"""
        if not user_has_permission(request.user, 'inventory_variant.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les variants',
                'required_permission': 'inventory_variant.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un variant - Nécessite inventory_variant.create"""
        if not user_has_permission(request.user, 'inventory_variant.create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des variants',
                'required_permission': 'inventory_variant.create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un variant - Nécessite inventory_variant.view"""
        if not user_has_permission(request.user, 'inventory_variant.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les variants',
                'required_permission': 'inventory_variant.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un variant - Nécessite inventory_variant.update"""
        if not user_has_permission(request.user, 'inventory_variant.update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les variants',
                'required_permission': 'inventory_variant.update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un variant - Nécessite inventory_variant.delete"""
        if not user_has_permission(request.user, 'inventory_variant.delete'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les variants',
                'required_permission': 'inventory_variant.delete'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


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
