from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Order, OrderItem, Invoice, ProformaInvoice, Payment
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderListSerializer,
    OrderItemSerializer, OrderItemCreateSerializer, OrderItemListSerializer,
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceListSerializer,
    ProformaInvoiceSerializer, ProformaInvoiceCreateSerializer, ProformaInvoiceListSerializer,
    PaymentSerializer, PaymentCreateSerializer, PaymentListSerializer
)
from apps.permissions.decorators import user_has_permission
from apps.common.mixins import CompanyFilterMixin


class OrderViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commandes - SÉCURISÉ
    """
    queryset = Order.objects.select_related('customer', 'user').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'status', 'user']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'notes']
    ordering_fields = ['created_at', 'order_date', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'list':
            return OrderListSerializer
        return OrderSerializer

    def list(self, request, *args, **kwargs):
        """Lister les commandes - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer une commande - Nécessite sales_order.create"""
        if not user_has_permission(request.user, 'sales_order.create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des commandes',
                'required_permission': 'sales_order.create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir une commande - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier une commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les commandes',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer une commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les commandes',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les commandes selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(order_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(order_date__date__lte=date_to)
            
        return queryset

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Lister uniquement les commandes en attente - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        pending_orders = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def confirmed(self, request):
        """Lister uniquement les commandes confirmées - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        confirmed_orders = self.get_queryset().filter(status='confirmed')
        serializer = self.get_serializer(confirmed_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def shipped(self, request):
        """Lister uniquement les commandes expédiées - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        shipped_orders = self.get_queryset().filter(status='shipped')
        serializer = self.get_serializer(shipped_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def delivered(self, request):
        """Lister uniquement les commandes livrées - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        delivered_orders = self.get_queryset().filter(status='delivered')
        serializer = self.get_serializer(delivered_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cancelled(self, request):
        """Lister uniquement les commandes annulées - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        cancelled_orders = self.get_queryset().filter(status='cancelled')
        serializer = self.get_serializer(cancelled_orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmer une commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les commandes',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        order.status = 'confirmed'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Marquer une commande comme expédiée - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les commandes',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        order.status = 'shipped'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Marquer une commande comme livrée - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les commandes',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        order.status = 'delivered'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler une commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les commandes',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        order = self.get_object()
        order.status = 'cancelled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des commandes - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les commandes',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_orders = queryset.count()
        pending_orders = queryset.filter(status='pending').count()
        confirmed_orders = queryset.filter(status='confirmed').count()
        shipped_orders = queryset.filter(status='shipped').count()
        delivered_orders = queryset.filter(status='delivered').count()
        cancelled_orders = queryset.filter(status='cancelled').count()
        
        # Chiffre d'affaires total
        total_revenue = queryset.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Commandes par statut
        by_status = queryset.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': total_revenue,
            'by_status': list(by_status),
        })


class OrderItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des articles de commande - SÉCURISÉ
    """
    queryset = OrderItem.objects.select_related('order', 'product', 'variant')
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['order', 'product', 'variant']
    search_fields = ['product__name', 'variant__name']
    ordering_fields = ['created_at', 'quantity', 'unit_price', 'total_price']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return OrderItemCreateSerializer
        elif self.action == 'list':
            return OrderItemListSerializer
        return OrderItemSerializer

    def list(self, request, *args, **kwargs):
        """Lister les articles de commande - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les articles de commande',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un article de commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des articles de commande',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un article de commande - Nécessite sales_order.view"""
        if not user_has_permission(request.user, 'sales_order.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les articles de commande',
                'required_permission': 'sales_order.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un article de commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les articles de commande',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un article de commande - Nécessite sales_orders_create"""
        if not user_has_permission(request.user, 'sales_orders_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les articles de commande',
                'required_permission': 'sales_orders_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des factures - SÉCURISÉ
    """
    queryset = Invoice.objects.select_related('order__customer', 'user')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'user']
    search_fields = ['invoice_number', 'order__customer__first_name', 'order__customer__last_name']
    ordering_fields = ['created_at', 'invoice_date', 'due_date', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return InvoiceCreateSerializer
        elif self.action == 'list':
            return InvoiceListSerializer
        return InvoiceSerializer

    def list(self, request, *args, **kwargs):
        """Lister les factures - Nécessite sales_invoice.view"""
        if not user_has_permission(request.user, 'sales_invoice.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoice.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer une facture - Nécessite sales_invoice.create"""
        if not user_has_permission(request.user, 'sales_invoice.create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des factures',
                'required_permission': 'sales_invoice.create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir une facture - Nécessite sales_invoice.view"""
        if not user_has_permission(request.user, 'sales_invoice.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoice.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier une facture - Nécessite sales_invoices_create"""
        if not user_has_permission(request.user, 'sales_invoices_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les factures',
                'required_permission': 'sales_invoices_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer une facture - Nécessite sales_invoices_create"""
        if not user_has_permission(request.user, 'sales_invoices_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les factures',
                'required_permission': 'sales_invoices_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les factures selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(invoice_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(invoice_date__date__lte=date_to)
            
        return queryset

    @action(detail=False, methods=['get'])
    def draft(self, request):
        """Lister uniquement les factures en brouillon - Nécessite sales_invoices_view"""
        if not user_has_permission(request.user, 'sales_invoices_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoices_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        draft_invoices = self.get_queryset().filter(status='draft')
        serializer = self.get_serializer(draft_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Lister uniquement les factures envoyées - Nécessite sales_invoices_view"""
        if not user_has_permission(request.user, 'sales_invoices_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoices_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        sent_invoices = self.get_queryset().filter(status='sent')
        serializer = self.get_serializer(sent_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def paid(self, request):
        """Lister uniquement les factures payées - Nécessite sales_invoices_view"""
        if not user_has_permission(request.user, 'sales_invoices_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoices_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        paid_invoices = self.get_queryset().filter(status='paid')
        serializer = self.get_serializer(paid_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Lister uniquement les factures en retard - Nécessite sales_invoices_view"""
        if not user_has_permission(request.user, 'sales_invoices_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoices_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        overdue_invoices = self.get_queryset().filter(
            status__in=['sent', 'partial'],
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Envoyer une facture - Nécessite sales_invoices_create"""
        if not user_has_permission(request.user, 'sales_invoices_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les factures',
                'required_permission': 'sales_invoices_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        invoice = self.get_object()
        invoice.status = 'sent'
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Marquer une facture comme payée - Nécessite sales_invoices_create"""
        if not user_has_permission(request.user, 'sales_invoices_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les factures',
                'required_permission': 'sales_invoices_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.paid_amount = invoice.total_amount
        invoice.remaining_amount = 0
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des factures - Nécessite sales_invoice.view"""
        if not user_has_permission(request.user, 'sales_invoice.view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les factures',
                'required_permission': 'sales_invoice.view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            today = timezone.now().date()
            
            # Statistiques générales
            total_invoices = Invoice.objects.count()
            paid_invoices = Invoice.objects.filter(status='paid').count()
            pending_invoices = Invoice.objects.filter(status='pending').count()
            overdue_invoices = Invoice.objects.filter(
                status='pending',
                due_date__lt=today
            ).count()
            cancelled_invoices = Invoice.objects.filter(status='cancelled').count()
            
            # Montants
            total_amount = Invoice.objects.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            paid_amount = Invoice.objects.filter(status='paid').aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            pending_amount = Invoice.objects.filter(status='pending').aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0.00')
            
            overdue_amount = Invoice.objects.filter(
                status='pending',
                due_date__lt=today
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            # Taux de recouvrement
            collection_rate = 0.0
            if total_amount > 0:
                collection_rate = (paid_amount / total_amount) * 100
            
            data = {
                "invoices": {
                    "total": total_invoices,
                    "paid": paid_invoices,
                    "pending": pending_invoices,
                    "overdue": overdue_invoices,
                    "cancelled": cancelled_invoices
                },
                "amounts": {
                    "total": float(total_amount),
                    "paid": float(paid_amount),
                    "pending": float(pending_amount),
                    "overdue": float(overdue_amount)
                },
                "collection_rate": round(collection_rate, 2)
            }
            
            return Response({
                "success": True,
                "data": data
            })
            
        except Exception as e:
            return Response({
                "success": False,
                "error": {
                    "code": "INVOICES_SUMMARY_ERROR",
                    "message": "Erreur lors de la récupération du résumé des factures",
                    "details": str(e)
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProformaInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des devis - SÉCURISÉ
    """
    queryset = ProformaInvoice.objects.select_related('customer', 'user')
    serializer_class = ProformaInvoiceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'status', 'user']
    search_fields = ['proforma_number', 'customer__first_name', 'customer__last_name']
    ordering_fields = ['created_at', 'proforma_date', 'valid_until', 'total_amount']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return ProformaInvoiceCreateSerializer
        elif self.action == 'list':
            return ProformaInvoiceListSerializer
        return ProformaInvoiceSerializer

    def list(self, request, *args, **kwargs):
        """Lister les devis - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un devis - Nécessite sales_proformas_create"""
        if not user_has_permission(request.user, 'sales_proformas_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des devis',
                'required_permission': 'sales_proformas_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un devis - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un devis - Nécessite sales_proformas_create"""
        if not user_has_permission(request.user, 'sales_proformas_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les devis',
                'required_permission': 'sales_proformas_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un devis - Nécessite sales_proformas_create"""
        if not user_has_permission(request.user, 'sales_proformas_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les devis',
                'required_permission': 'sales_proformas_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les devis selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(proforma_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(proforma_date__date__lte=date_to)
            
        return queryset

    @action(detail=False, methods=['get'])
    def draft(self, request):
        """Lister uniquement les devis en brouillon - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        draft_proformas = self.get_queryset().filter(status='draft')
        serializer = self.get_serializer(draft_proformas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Lister uniquement les devis envoyés - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        sent_proformas = self.get_queryset().filter(status='sent')
        serializer = self.get_serializer(sent_proformas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def accepted(self, request):
        """Lister uniquement les devis acceptés - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        accepted_proformas = self.get_queryset().filter(status='accepted')
        serializer = self.get_serializer(accepted_proformas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Lister uniquement les devis expirés - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        expired_proformas = self.get_queryset().filter(valid_until__lt=timezone.now())
        serializer = self.get_serializer(expired_proformas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Envoyer un devis - Nécessite sales_proformas_create"""
        if not user_has_permission(request.user, 'sales_proformas_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les devis',
                'required_permission': 'sales_proformas_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        proforma = self.get_object()
        proforma.status = 'sent'
        proforma.save()
        
        serializer = self.get_serializer(proforma)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accepter un devis - Nécessite sales_proformas_create"""
        if not user_has_permission(request.user, 'sales_proformas_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les devis',
                'required_permission': 'sales_proformas_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        proforma = self.get_object()
        proforma.status = 'accepted'
        proforma.save()
        
        serializer = self.get_serializer(proforma)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter un devis - Nécessite sales_proformas_create"""
        if not user_has_permission(request.user, 'sales_proformas_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les devis',
                'required_permission': 'sales_proformas_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        proforma = self.get_object()
        proforma.status = 'rejected'
        proforma.save()
        
        serializer = self.get_serializer(proforma)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des devis - Nécessite sales_proformas_view"""
        if not user_has_permission(request.user, 'sales_proformas_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les devis',
                'required_permission': 'sales_proformas_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_proformas = queryset.count()
        draft_proformas = queryset.filter(status='draft').count()
        sent_proformas = queryset.filter(status='sent').count()
        accepted_proformas = queryset.filter(status='accepted').count()
        rejected_proformas = queryset.filter(status='rejected').count()
        expired_proformas = queryset.filter(valid_until__lt=timezone.now()).count()
        
        # Montant total
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        
        return Response({
            'total_proformas': total_proformas,
            'draft_proformas': draft_proformas,
            'sent_proformas': sent_proformas,
            'accepted_proformas': accepted_proformas,
            'rejected_proformas': rejected_proformas,
            'expired_proformas': expired_proformas,
            'total_amount': total_amount,
        })


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des paiements - SÉCURISÉ
    """
    queryset = Payment.objects.select_related('invoice__order__customer', 'user')
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['invoice', 'payment_method', 'user']
    search_fields = ['invoice__invoice_number', 'reference', 'notes']
    ordering_fields = ['created_at', 'payment_date', 'amount']
    ordering = ['-payment_date']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        return PaymentSerializer

    def list(self, request, *args, **kwargs):
        """Lister les paiements - Nécessite sales_payments_view"""
        if not user_has_permission(request.user, 'sales_payments_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les paiements',
                'required_permission': 'sales_payments_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un paiement - Nécessite sales_payments_create"""
        if not user_has_permission(request.user, 'sales_payments_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des paiements',
                'required_permission': 'sales_payments_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un paiement - Nécessite sales_payments_view"""
        if not user_has_permission(request.user, 'sales_payments_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les paiements',
                'required_permission': 'sales_payments_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un paiement - Nécessite sales_payments_create"""
        if not user_has_permission(request.user, 'sales_payments_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les paiements',
                'required_permission': 'sales_payments_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un paiement - Nécessite sales_payments_create"""
        if not user_has_permission(request.user, 'sales_payments_create'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les paiements',
                'required_permission': 'sales_payments_create'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les paiements selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(payment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(payment_date__date__lte=date_to)
            
        return queryset

    @action(detail=False, methods=['get'])
    def by_method(self, request):
        """Lister les paiements par méthode - Nécessite sales_payments_view"""
        if not user_has_permission(request.user, 'sales_payments_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les paiements',
                'required_permission': 'sales_payments_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        method = request.query_params.get('method')
        if method:
            payments = self.get_queryset().filter(payment_method=method)
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        return Response({'error': 'Méthode de paiement requise'}, status=400)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des paiements - Nécessite sales_payments_view"""
        if not user_has_permission(request.user, 'sales_payments_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les paiements',
                'required_permission': 'sales_payments_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_payments = queryset.count()
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        # Paiements par méthode
        by_method = queryset.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')
        
        return Response({
            'total_payments': total_payments,
            'total_amount': total_amount,
            'by_method': list(by_method),
        })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_sales_endpoint(request):
    """
    Endpoint de test pour l'API Sales
    """
    if request.method == 'GET':
        return Response({
            'message': 'API Sales fonctionne correctement !',
            'endpoints': [
                'GET /api/sales/orders/ - Lister les commandes',
                'POST /api/sales/orders/ - Créer une commande',
                'GET /api/sales/invoices/ - Lister les factures',
                'POST /api/sales/invoices/ - Créer une facture',
                'GET /api/sales/proformas/ - Lister les devis',
                'POST /api/sales/proformas/ - Créer un devis',
                'GET /api/sales/payments/ - Lister les paiements',
                'POST /api/sales/payments/ - Créer un paiement',
            ]
        })
    
    elif request.method == 'POST':
        return Response({
            'message': 'Test POST réussi !',
            'data': request.data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_summary(request):
    """
    Résumé des commandes pour le dashboard.
    """
    # Vérifier la permission
    if not user_has_permission(request.user, 'sales_order.view'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de voir les commandes',
            'required_permission': 'sales_order.view'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Statistiques générales
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        confirmed_orders = Order.objects.filter(status='confirmed').count()
        shipped_orders = Order.objects.filter(status='shipped').count()
        delivered_orders = Order.objects.filter(status='delivered').count()
        cancelled_orders = Order.objects.filter(status='cancelled').count()
        
        # Revenus par période
        revenue_today = Order.objects.filter(
            created_at__date=today,
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        revenue_week = Order.objects.filter(
            created_at__date__gte=week_ago,
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        revenue_month = Order.objects.filter(
            created_at__date__gte=month_ago,
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Calcul de la croissance
        previous_month_start = month_ago - timedelta(days=30)
        previous_month_revenue = Order.objects.filter(
            created_at__date__gte=previous_month_start,
            created_at__date__lt=month_ago,
            status__in=['confirmed', 'shipped', 'delivered']
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        growth = 0.0
        if previous_month_revenue > 0:
            growth = float(((revenue_month - previous_month_revenue) / previous_month_revenue) * 100)
        
        # Taux de conversion
        conversion_rate = 0.0
        if total_orders > 0:
            conversion_rate = (delivered_orders / total_orders) * 100
        
        data = {
            "orders": {
                "total": total_orders,
                "pending": pending_orders,
                "confirmed": confirmed_orders,
                "shipped": shipped_orders,
                "delivered": delivered_orders,
                "cancelled": cancelled_orders
            },
            "revenue": {
                "today": float(revenue_today),
                "week": float(revenue_week),
                "month": float(revenue_month),
                "growth": round(growth, 2)
            },
            "conversion_rate": round(conversion_rate, 2)
        }
        
        return Response({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "ORDERS_SUMMARY_ERROR",
                "message": "Erreur lors de la récupération du résumé des commandes",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoices_summary(request):
    """
    Résumé des factures pour le dashboard.
    """
    # Vérifier la permission
    if not user_has_permission(request.user, 'sales_invoice.view'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de voir les factures',
            'required_permission': 'sales_invoice.view'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        today = timezone.now().date()
        
        # Statistiques générales
        total_invoices = Invoice.objects.count()
        paid_invoices = Invoice.objects.filter(status='paid').count()
        pending_invoices = Invoice.objects.filter(status='pending').count()
        overdue_invoices = Invoice.objects.filter(
            status='pending',
            due_date__lt=today
        ).count()
        cancelled_invoices = Invoice.objects.filter(status='cancelled').count()
        
        # Montants
        total_amount = Invoice.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        paid_amount = Invoice.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        pending_amount = Invoice.objects.filter(status='pending').aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        overdue_amount = Invoice.objects.filter(
            status='pending',
            due_date__lt=today
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Taux de recouvrement
        collection_rate = 0.0
        if total_amount > 0:
            collection_rate = (paid_amount / total_amount) * 100
        
        data = {
            "invoices": {
                "total": total_invoices,
                "paid": paid_invoices,
                "pending": pending_invoices,
                "overdue": overdue_invoices,
                "cancelled": cancelled_invoices
            },
            "amounts": {
                "total": float(total_amount),
                "paid": float(paid_amount),
                "pending": float(pending_amount),
                "overdue": float(overdue_amount)
            },
            "collection_rate": round(collection_rate, 2)
        }
        
        return Response({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "INVOICES_SUMMARY_ERROR",
                "message": "Erreur lors de la récupération du résumé des factures",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)