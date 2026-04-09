from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count, Sum, Max
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Customer
from .serializers import (
    CustomerSerializer,
    CustomerListSerializer,
    CustomerCreateSerializer,
    CustomerKPIsSerializer
)
from apps.permissions.decorators import require_permission, user_has_permission
from apps.common.mixins import CompanyFilterMixin


class CustomerPagination(PageNumberPagination):
    """
    Pagination personnalisée pour les clients
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'
    
    def get_page_size(self, request):
        """
        Valider les tailles de page autorisées
        """
        if self.page_size_query_param:
            page_size = request.query_params.get(self.page_size_query_param)
            if page_size is not None:
                try:
                    page_size = int(page_size)
                    # Tailles autorisées : 5, 10, 25, 50
                    if page_size in [5, 10, 25, 50]:
                        return page_size
                except (KeyError, ValueError):
                    pass
        return self.page_size


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """
    Endpoint de test pour vérifier que l'API fonctionne
    """
    if request.method == 'GET':
        return Response({
            'message': 'API Customers fonctionne !',
            'method': 'GET',
            'status': 'success'
        })
    elif request.method == 'POST':
        return Response({
            'message': 'API Customers fonctionne !',
            'method': 'POST',
            'data_received': request.data,
            'status': 'success'
        })


class CustomerViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clients - SÉCURISÉ
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = CustomerPagination
    
    # Filtres
    filterset_fields = ['is_active', 'city', 'client_company']
    search_fields = ['first_name', 'last_name', 'email', 'client_company', 'phone']
    ordering_fields = [
        'first_name', 'last_name', 'email', 'created_at', 'updated_at'
    ]
    ordering = ['last_name', 'first_name']

    def get_serializer_class(self):
        """
        Retourne le serializer approprié selon l'action
        """
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'create':
            return CustomerCreateSerializer
        return CustomerSerializer

    def list(self, request, *args, **kwargs):
        """
        Lister les clients - Nécessite la permission customers_view
        """
        if not user_has_permission(request.user, 'customers_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les clients',
                'required_permission': 'customers_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Récupérer le queryset de base
        queryset = self.get_queryset()
        
        # Appliquer tous les filtres (y compris la recherche personnalisée)
        queryset = self.filter_queryset(queryset)
        
        # Gérer le tri (tous les types)
        ordering = request.query_params.get('ordering')
        if ordering:
            if ordering in ['total_orders', '-total_orders', 'total_spent', '-total_spent', 'last_order_date', '-last_order_date']:
                # Tri par champs calculés
                if ordering in ['total_orders', '-total_orders']:
                    queryset = queryset.order_by('order_count' if ordering == 'total_orders' else '-order_count')
                elif ordering in ['total_spent', '-total_spent']:
                    queryset = queryset.order_by('total_spent_amount' if ordering == 'total_spent' else '-total_spent_amount')
                elif ordering in ['last_order_date', '-last_order_date']:
                    queryset = queryset.order_by('last_order_date_field' if ordering == 'last_order_date' else '-last_order_date_field')
            elif ordering in ['created_at', '-created_at']:
                # Tri par date de création
                queryset = queryset.order_by(ordering)
            else:
                # Tri par autres champs normaux (géré par Django REST Framework)
                queryset = queryset.order_by(ordering)
        
        # Appliquer la pagination avec le count correct
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            # Mettre à jour le count pour refléter les résultats filtrés
            response.data['count'] = queryset.count()
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Créer un client - Nécessite la permission customers_create
        """
        if not user_has_permission(request.user, 'customers_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des clients',
                'required_permission': 'customers_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Appeler perform_create() du mixin pour assigner automatiquement le company
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def retrieve(self, request, *args, **kwargs):
        """
        Voir un client - Nécessite la permission customers_view
        """
        if not user_has_permission(request.user, 'customers_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les clients',
                'required_permission': 'customers_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Modifier un client - Nécessite la permission customers_update
        """
        if not user_has_permission(request.user, 'customers_update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les clients',
                'required_permission': 'customers_update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Supprimer un client - Nécessite la permission customers_delete
        """
        if not user_has_permission(request.user, 'customers_delete'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les clients',
                'required_permission': 'customers_delete'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filtre les clients selon les paramètres de recherche
        Le filtrage par Company est géré automatiquement par CompanyFilterMixin
        """
        # D'abord appliquer le filtrage par Company du mixin
        queryset = super().get_queryset()
        
        # Optimiser les requêtes pour éviter les N+1
        queryset = queryset.select_related('company')
        
        # Ajouter les annotations pour les champs calculés si nécessaire
        ordering = self.request.query_params.get('ordering')
        if ordering and ordering in ['total_orders', '-total_orders', 'total_spent', '-total_spent', 'last_order_date', '-last_order_date']:
            try:
                from apps.sales.models import Order
                if ordering in ['total_orders', '-total_orders']:
                    queryset = queryset.annotate(
                        order_count=Count('order', filter=Q(order__status__in=['confirmed', 'shipped', 'delivered']))
                    )
                elif ordering in ['total_spent', '-total_spent']:
                    queryset = queryset.annotate(
                        total_spent_amount=Sum('order__total_amount', filter=Q(order__status__in=['confirmed', 'shipped', 'delivered']))
                    )
                elif ordering in ['last_order_date', '-last_order_date']:
                    queryset = queryset.annotate(
                        last_order_date_field=Max('order__created_at', filter=Q(order__status__in=['confirmed', 'shipped', 'delivered']))
                    )
            except ImportError:
                pass
        
        # Filtre par statut actif
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filtre par pays
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        # Filtre par ville
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__icontains=city)
        
        # Filtre par entreprise du client (client_company)
        client_company = self.request.query_params.get('client_company')
        if client_company:
            queryset = queryset.filter(client_company__icontains=client_company)
        
        # Filtre par type de client
        customer_type = self.request.query_params.get('customer_type')
        if customer_type:
            if customer_type == 'individual':
                queryset = queryset.filter(Q(client_company__isnull=True) | Q(client_company=''))
            elif customer_type == 'business':
                queryset = queryset.filter(client_company__isnull=False).exclude(client_company='')
        
        return queryset

    def filter_queryset(self, queryset):
        """
        Appliquer les filtres personnalisés
        """
        # Appliquer les autres filtres
        queryset = super().filter_queryset(queryset)
        
        # Gérer la recherche dans le nom complet
        search = self.request.query_params.get('search')
        if search and search.strip():
            search_terms = search.strip().split()
            if len(search_terms) == 1:
                # Recherche simple
                queryset = queryset.filter(
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(phone__icontains=search) |
                    Q(company__icontains=search)
                )
            elif len(search_terms) >= 2:
                # Recherche par prénom et nom
                first_term = search_terms[0]
                last_term = search_terms[-1]
                queryset = queryset.filter(
                    Q(first_name__icontains=first_term) & Q(last_name__icontains=last_term) |
                    Q(first_name__icontains=last_term) & Q(last_name__icontains=first_term) |
                    Q(first_name__icontains=search) |
                    Q(last_name__icontains=search) |
                    Q(email__icontains=search) |
                    Q(phone__icontains=search) |
                    Q(company__icontains=search)
                )
        
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Retourne uniquement les clients actifs - Nécessite customers_view
        """
        if not user_has_permission(request.user, 'customers_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les clients',
                'required_permission': 'customers_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_customers = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inactive(self, request):
        """
        Retourne uniquement les clients inactifs - Nécessite customers_view
        """
        if not user_has_permission(request.user, 'customers_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les clients',
                'required_permission': 'customers_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        inactive_customers = self.get_queryset().filter(is_active=False)
        serializer = self.get_serializer(inactive_customers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Active un client - Nécessite customers_update
        """
        if not user_has_permission(request.user, 'customers_update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les clients',
                'required_permission': 'customers_update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        customer = self.get_object()
        customer.is_active = True
        customer.save()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Désactive un client - Nécessite customers_update
        """
        if not user_has_permission(request.user, 'customers_update'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les clients',
                'required_permission': 'customers_update'
            }, status=status.HTTP_403_FORBIDDEN)
        
        customer = self.get_object()
        customer.is_active = False
        customer.save()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Recherche avancée de clients - Nécessite customers_view
        """
        if not user_has_permission(request.user, 'customers_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les clients',
                'required_permission': 'customers_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Paramètre de recherche requis'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        customers = self.get_queryset().filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(company__icontains=query) |
            Q(phone__icontains=query)
        )
        
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Actions à effectuer lors de la création d'un client
        """
        serializer.save()

    def perform_update(self, serializer):
        """
        Actions à effectuer lors de la mise à jour d'un client
        """
        serializer.save()

    def perform_destroy(self, instance):
        """
        Actions à effectuer lors de la suppression d'un client
        """
        # Au lieu de supprimer, on désactive le client
        instance.is_active = False
        instance.save()


def get_date_range(period, custom_start_date=None, custom_end_date=None):
    """Calculer la plage de dates selon la période"""
    now = timezone.now().date()
    
    if period == '7d':
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == '30d':
        start_date = now - timedelta(days=30)
        end_date = now
    elif period == '90d':
        start_date = now - timedelta(days=90)
        end_date = now
    elif period == '1y':
        start_date = now - timedelta(days=365)
        end_date = now
    elif period == 'custom':
        if not custom_start_date or not custom_end_date:
            raise ValueError("custom_start_date et custom_end_date sont requis pour la période custom")
        start_date = datetime.strptime(custom_start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(custom_end_date, '%Y-%m-%d').date()
    else:
        raise ValueError("Période invalide. Utilisez 7d, 30d, 90d, 1y ou custom")
    
    return start_date, end_date


def get_customer_revenue(customer_id, start_date, end_date):
    """Calculer le revenu total d'un client pour une période donnée"""
    try:
        from apps.sales.models import Order
        revenue = Order.objects.filter(
            customer_id=customer_id,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total']
        return revenue or Decimal('0.00')
    except ImportError:
        # Si l'app sales n'est pas disponible, retourner 0
        return Decimal('0.00')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customers_analytics_kpis(request):
    """
    Endpoint pour les KPIs des clients
    """
    try:
        # Vérifier la permission
        if not user_has_permission(request.user, 'customers_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les clients',
                'required_permission': 'customers_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        from apps.permissions.decorators import user_has_permission as check_permission
        
        user_company = None
        if not check_permission(request.user, 'companies_view_all'):
            try:
                user_company = request.user.userprofile.company
            except AttributeError:
                return Response({
                    'error': 'Profil utilisateur manquant',
                    'detail': 'Vous n\'avez pas de profil utilisateur associé'
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Filtrage par company si nécessaire
        customer_filter = {}
        order_filter = {}
        
        if user_company:
            customer_filter['company'] = user_company
            order_filter['company'] = user_company
        
        # Calculer les KPIs avec filtrage par company
        total_clients = Customer.objects.filter(**customer_filter).count()
        active_clients = Customer.objects.filter(is_active=True, **customer_filter).count()
        companies = Customer.objects.filter(client_company__isnull=False, **customer_filter).exclude(client_company='').count()
        
        # Calculer le pourcentage de clients actifs
        active_clients_percentage = (active_clients / total_clients * 100) if total_clients > 0 else 0
        
        # Calculer le pourcentage d'entreprises
        companies_percentage = (companies / total_clients * 100) if total_clients > 0 else 0
        
        # Calculer le revenu total pour la période (filtré par company)
        total_revenue = Decimal('0.00')
        try:
            from apps.sales.models import Order
            revenue_data = Order.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                status__in=['confirmed', 'shipped', 'delivered'],
                **order_filter
            ).aggregate(total=Sum('total_amount'))
            total_revenue = revenue_data['total'] or Decimal('0.00')
        except ImportError:
            # Si l'app sales n'est pas disponible, utiliser des données d'exemple
            total_revenue = Decimal('4587781.00')
        
        # Calculer la croissance des clients (filtré par company)
        # Comparer avec la période précédente de même durée
        period_days = (end_date - start_date).days
        previous_start_date = start_date - timedelta(days=period_days)
        previous_end_date = start_date
        
        previous_total_clients = Customer.objects.filter(
            created_at__date__lt=start_date,
            **customer_filter
        ).count()
        
        total_clients_growth = 0.0
        if previous_total_clients > 0:
            new_clients_in_period = Customer.objects.filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date,
                **customer_filter
            ).count()
            total_clients_growth = (new_clients_in_period / previous_total_clients) * 100
        
        # Préparer la réponse
        kpis_data = {
            'total_clients': total_clients,
            'total_clients_growth': round(total_clients_growth, 1),
            'active_clients': active_clients,
            'active_clients_percentage': round(active_clients_percentage, 1),
            'companies': companies,
            'companies_percentage': round(companies_percentage, 1),
            'total_revenue': int(total_revenue),
            'revenue_currency': 'FCFA',
            'revenue_description': 'Tous clients confondus'
        }
        
        # Valider avec le serializer
        serializer = CustomerKPIsSerializer(kpis_data)
        
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
