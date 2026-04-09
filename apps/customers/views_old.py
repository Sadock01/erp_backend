from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from .models import Customer
from .serializers import (
    CustomerSerializer,
    CustomerListSerializer,
    CustomerCreateSerializer
)
from apps.permissions.permissions import (
    HasPermission, HasAnyPermission, 
    CustomersPermissions
)


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


@api_view(['POST'])
@permission_classes([AllowAny])
def create_customer_test(request):
    """
    Endpoint temporaire pour créer un client sans authentification (pour test)
    """
    serializer = CustomerCreateSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        response_serializer = CustomerSerializer(customer)
        return Response({
            'message': 'Client créé avec succès !',
            'customer': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'error': 'Erreur de validation',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des clients
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Filtres
    filterset_fields = ['is_active', 'country', 'company']
    search_fields = ['first_name', 'last_name', 'email', 'company', 'phone']
    ordering_fields = ['first_name', 'last_name', 'email', 'created_at', 'updated_at']
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

    def get_queryset(self):
        """
        Filtre les clients selon les paramètres de recherche
        """
        queryset = Customer.objects.all()
        
        # Filtre par statut actif
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filtre par pays
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country__icontains=country)
        
        # Filtre par entreprise
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(company__icontains=company)
        
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Retourne uniquement les clients actifs
        """
        active_customers = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_customers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def inactive(self, request):
        """
        Retourne uniquement les clients inactifs
        """
        inactive_customers = self.get_queryset().filter(is_active=False)
        serializer = self.get_serializer(inactive_customers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Active un client
        """
        customer = self.get_object()
        customer.is_active = True
        customer.save()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Désactive un client
        """
        customer = self.get_object()
        customer.is_active = False
        customer.save()
        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Recherche avancée de clients
        """
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
