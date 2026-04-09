from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, F, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Order, OrderItem, Invoice, ProformaInvoice, Payment
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderListSerializer,
    OrderItemSerializer, OrderItemCreateSerializer, OrderItemListSerializer,
    InvoiceSerializer, InvoiceCreateSerializer, InvoiceListSerializer,
    ProformaInvoiceSerializer, ProformaInvoiceCreateSerializer, ProformaInvoiceListSerializer,
    PaymentSerializer, PaymentCreateSerializer, PaymentListSerializer
)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des commandes
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
        """Lister uniquement les commandes en attente"""
        pending_orders = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def confirmed(self, request):
        """Lister uniquement les commandes confirmées"""
        confirmed_orders = self.get_queryset().filter(status='confirmed')
        serializer = self.get_serializer(confirmed_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def shipped(self, request):
        """Lister uniquement les commandes expédiées"""
        shipped_orders = self.get_queryset().filter(status='shipped')
        serializer = self.get_serializer(shipped_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def delivered(self, request):
        """Lister uniquement les commandes livrées"""
        delivered_orders = self.get_queryset().filter(status='delivered')
        serializer = self.get_serializer(delivered_orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def cancelled(self, request):
        """Lister uniquement les commandes annulées"""
        cancelled_orders = self.get_queryset().filter(status='cancelled')
        serializer = self.get_serializer(cancelled_orders, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirmer une commande"""
        order = self.get_object()
        order.status = 'confirmed'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def ship(self, request, pk=None):
        """Marquer une commande comme expédiée"""
        order = self.get_object()
        order.status = 'shipped'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deliver(self, request, pk=None):
        """Marquer une commande comme livrée"""
        order = self.get_object()
        order.status = 'delivered'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Annuler une commande"""
        order = self.get_object()
        order.status = 'cancelled'
        order.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des commandes"""
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
    ViewSet pour la gestion des articles de commande
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


class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des factures
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
        """Lister uniquement les factures en brouillon"""
        draft_invoices = self.get_queryset().filter(status='draft')
        serializer = self.get_serializer(draft_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Lister uniquement les factures envoyées"""
        sent_invoices = self.get_queryset().filter(status='sent')
        serializer = self.get_serializer(sent_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def paid(self, request):
        """Lister uniquement les factures payées"""
        paid_invoices = self.get_queryset().filter(status='paid')
        serializer = self.get_serializer(paid_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Lister uniquement les factures en retard"""
        overdue_invoices = self.get_queryset().filter(
            status__in=['sent', 'partial'],
            due_date__lt=timezone.now().date()
        )
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Envoyer une facture"""
        invoice = self.get_object()
        invoice.status = 'sent'
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Marquer une facture comme payée"""
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.paid_amount = invoice.total_amount
        invoice.remaining_amount = 0
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des factures"""
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_invoices = queryset.count()
        draft_invoices = queryset.filter(status='draft').count()
        sent_invoices = queryset.filter(status='sent').count()
        paid_invoices = queryset.filter(status='paid').count()
        overdue_invoices = queryset.filter(
            status__in=['sent', 'partial'],
            due_date__lt=timezone.now().date()
        ).count()
        
        # Montants totaux
        total_amount = queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        paid_amount = queryset.aggregate(total=Sum('paid_amount'))['total'] or 0
        remaining_amount = queryset.aggregate(total=Sum('remaining_amount'))['total'] or 0
        
        return Response({
            'total_invoices': total_invoices,
            'draft_invoices': draft_invoices,
            'sent_invoices': sent_invoices,
            'paid_invoices': paid_invoices,
            'overdue_invoices': overdue_invoices,
            'total_amount': total_amount,
            'paid_amount': paid_amount,
            'remaining_amount': remaining_amount,
        })


class ProformaInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des devis
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
        """Lister uniquement les devis en brouillon"""
        draft_proformas = self.get_queryset().filter(status='draft')
        serializer = self.get_serializer(draft_proformas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Lister uniquement les devis envoyés"""
        sent_proformas = self.get_queryset().filter(status='sent')
        serializer = self.get_serializer(sent_proformas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def accepted(self, request):
        """Lister uniquement les devis acceptés"""
        accepted_proformas = self.get_queryset().filter(status='accepted')
        serializer = self.get_serializer(accepted_proformas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Lister uniquement les devis expirés"""
        expired_proformas = self.get_queryset().filter(valid_until__lt=timezone.now())
        serializer = self.get_serializer(expired_proformas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def send(self, request, pk=None):
        """Envoyer un devis"""
        proforma = self.get_object()
        proforma.status = 'sent'
        proforma.save()
        
        serializer = self.get_serializer(proforma)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accepter un devis"""
        proforma = self.get_object()
        proforma.status = 'accepted'
        proforma.save()
        
        serializer = self.get_serializer(proforma)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter un devis"""
        proforma = self.get_object()
        proforma.status = 'rejected'
        proforma.save()
        
        serializer = self.get_serializer(proforma)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des devis"""
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
    ViewSet pour la gestion des paiements
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
        """Lister les paiements par méthode"""
        method = request.query_params.get('method')
        if method:
            payments = self.get_queryset().filter(payment_method=method)
            serializer = self.get_serializer(payments, many=True)
            return Response(serializer.data)
        return Response({'error': 'Méthode de paiement requise'}, status=400)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des paiements"""
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