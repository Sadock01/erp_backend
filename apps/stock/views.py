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

from .models import StockMovement, StockAdjustment, StockAlert, StockReport
from .serializers import (
    StockMovementSerializer, StockMovementCreateSerializer, StockMovementListSerializer,
    StockAdjustmentSerializer, StockAdjustmentCreateSerializer, StockAdjustmentListSerializer,
    StockAlertSerializer, StockAlertListSerializer,
    StockReportSerializer
)
from apps.permissions.decorators import user_has_permission
from apps.common.mixins import CompanyFilterMixin


class StockMovementViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des mouvements de stock - SÉCURISÉ
    """
    queryset = StockMovement.objects.select_related('product', 'variant', 'user', 'approved_by')
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'variant', 'movement_type', 'is_approved', 'user']
    search_fields = ['product__name', 'variant__name', 'reference', 'notes']
    ordering_fields = ['created_at', 'quantity', 'total_cost']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return StockMovementCreateSerializer
        elif self.action == 'list':
            return StockMovementListSerializer
        return StockMovementSerializer

    def list(self, request, *args, **kwargs):
        """Lister les mouvements - Nécessite stock_view"""
        if not user_has_permission(request.user, 'stock_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les mouvements de stock',
                'required_permission': 'stock_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un mouvement - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des mouvements de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un mouvement - Nécessite stock_view"""
        if not user_has_permission(request.user, 'stock_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les mouvements de stock',
                'required_permission': 'stock_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un mouvement - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les mouvements de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un mouvement - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les mouvements de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les mouvements selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
            
        return queryset

    @action(detail=False, methods=['get'])
    def entries(self, request):
        """Lister uniquement les entrées de stock - Nécessite stock_view"""
        if not user_has_permission(request.user, 'stock_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les mouvements de stock',
                'required_permission': 'stock_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        entries = self.get_queryset().filter(quantity__gt=0)
        serializer = self.get_serializer(entries, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def exits(self, request):
        """Lister uniquement les sorties de stock - Nécessite stock_view"""
        if not user_has_permission(request.user, 'stock_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les mouvements de stock',
                'required_permission': 'stock_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        exits = self.get_queryset().filter(quantity__lt=0)
        serializer = self.get_serializer(exits, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Lister les mouvements en attente d'approbation - Nécessite stock_view"""
        if not user_has_permission(request.user, 'stock_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les mouvements de stock',
                'required_permission': 'stock_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        pending = self.get_queryset().filter(is_approved=False)
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver un mouvement de stock - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les mouvements de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        movement = self.get_object()
        movement.is_approved = True
        movement.approved_by = request.user
        movement.approved_at = timezone.now()
        movement.save()
        
        serializer = self.get_serializer(movement)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter un mouvement de stock - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les mouvements de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        movement = self.get_object()
        movement.is_approved = False
        movement.approved_by = request.user
        movement.approved_at = timezone.now()
        movement.save()
        
        serializer = self.get_serializer(movement)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des mouvements de stock - Nécessite stock_view"""
        if not user_has_permission(request.user, 'stock_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les mouvements de stock',
                'required_permission': 'stock_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_movements = queryset.count()
        total_entries = queryset.filter(quantity__gt=0).count()
        total_exits = queryset.filter(quantity__lt=0).count()
        
        # Quantités totales
        total_quantity_entries = queryset.filter(quantity__gt=0).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_quantity_exits = queryset.filter(quantity__lt=0).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # Coûts totaux
        total_cost_entries = queryset.filter(quantity__gt=0).aggregate(
            total=Sum('total_cost')
        )['total'] or 0
        
        total_cost_exits = queryset.filter(quantity__lt=0).aggregate(
            total=Sum('total_cost')
        )['total'] or 0
        
        return Response({
            'total_movements': total_movements,
            'total_entries': total_entries,
            'total_exits': total_exits,
            'total_quantity_entries': total_quantity_entries,
            'total_quantity_exits': total_quantity_exits,
            'total_cost_entries': total_cost_entries,
            'total_cost_exits': total_cost_exits,
        })


class StockAdjustmentViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des ajustements de stock - SÉCURISÉ
    """
    queryset = StockAdjustment.objects.select_related('product', 'variant', 'user', 'approved_by')
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'variant', 'adjustment_type', 'is_approved', 'user']
    search_fields = ['product__name', 'variant__name', 'reason']
    ordering_fields = ['created_at', 'adjustment_quantity']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'create':
            return StockAdjustmentCreateSerializer
        elif self.action == 'list':
            return StockAdjustmentListSerializer
        return StockAdjustmentSerializer

    def list(self, request, *args, **kwargs):
        """Lister les ajustements - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un ajustement - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un ajustement - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un ajustement - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un ajustement - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les ajustements selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
            
        return queryset

    @action(detail=False, methods=['get'])
    def pending_approval(self, request):
        """Lister les ajustements en attente d'approbation - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        pending = self.get_queryset().filter(is_approved=False)
        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approuver un ajustement de stock - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        adjustment = self.get_object()
        adjustment.is_approved = True
        adjustment.approved_by = request.user
        adjustment.approved_at = timezone.now()
        adjustment.save()
        
        serializer = self.get_serializer(adjustment)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Rejeter un ajustement de stock - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        adjustment = self.get_object()
        adjustment.is_approved = False
        adjustment.approved_by = request.user
        adjustment.approved_at = timezone.now()
        adjustment.save()
        
        serializer = self.get_serializer(adjustment)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des ajustements de stock - Nécessite stock_adjust"""
        if not user_has_permission(request.user, 'stock_adjust'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les ajustements de stock',
                'required_permission': 'stock_adjust'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_adjustments = queryset.count()
        pending_approval = queryset.filter(is_approved=False).count()
        approved = queryset.filter(is_approved=True).count()
        
        # Ajustements par type
        by_type = queryset.values('adjustment_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_adjustments': total_adjustments,
            'pending_approval': pending_approval,
            'approved': approved,
            'by_type': list(by_type),
        })


class StockAlertViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des alertes de stock - SÉCURISÉ
    """
    queryset = StockAlert.objects.select_related('product', 'variant', 'resolved_by')
    serializer_class = StockAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['product', 'variant', 'alert_type', 'is_active', 'is_resolved']
    search_fields = ['product__name', 'variant__name']
    ordering_fields = ['created_at', 'current_quantity', 'threshold_quantity']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Sélectionner le serializer approprié"""
        if self.action == 'list':
            return StockAlertListSerializer
        return StockAlertSerializer

    def list(self, request, *args, **kwargs):
        """Lister les alertes - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer une alerte - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir une alerte - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier une alerte - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer une alerte - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lister uniquement les alertes actives - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_alerts = self.get_queryset().filter(is_active=True, is_resolved=False)
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def resolved(self, request):
        """Lister uniquement les alertes résolues - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        resolved_alerts = self.get_queryset().filter(is_resolved=True)
        serializer = self.get_serializer(resolved_alerts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Résoudre une alerte de stock - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        alert = self.get_object()
        alert.is_resolved = True
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        
        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des alertes de stock - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les alertes de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_alerts = queryset.count()
        active_alerts = queryset.filter(is_active=True, is_resolved=False).count()
        resolved_alerts = queryset.filter(is_resolved=True).count()
        
        # Alertes par type
        by_type = queryset.values('alert_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': resolved_alerts,
            'by_type': list(by_type),
        })


class StockReportViewSet(CompanyFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des rapports de stock - SÉCURISÉ
    """
    queryset = StockReport.objects.select_related('user')
    serializer_class = StockReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['report_type', 'is_generated', 'user']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'generated_at']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        """Lister les rapports - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un rapport - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un rapport - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un rapport - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un rapport - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        """Filtrer les rapports selon les permissions"""
        queryset = super().get_queryset()
        
        # Filtrer par date si fournie
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date_from__gte=date_from)
        if date_to:
            queryset = queryset.filter(date_to__lte=date_to)
            
        return queryset

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Générer un rapport de stock - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        report = self.get_object()
        
        # Ici vous pouvez implémenter la logique de génération du rapport
        # Pour l'instant, on simule juste la génération
        report.is_generated = True
        report.generated_at = timezone.now()
        report.data = {
            'generated_at': timezone.now().isoformat(),
            'status': 'success',
            'message': 'Rapport généré avec succès'
        }
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des rapports de stock - Nécessite stock_manage"""
        if not user_has_permission(request.user, 'stock_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rapports de stock',
                'required_permission': 'stock_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_reports = queryset.count()
        generated_reports = queryset.filter(is_generated=True).count()
        pending_reports = queryset.filter(is_generated=False).count()
        
        # Rapports par type
        by_type = queryset.values('report_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        return Response({
            'total_reports': total_reports,
            'generated_reports': generated_reports,
            'pending_reports': pending_reports,
            'by_type': list(by_type),
        })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_stock_endpoint(request):
    """
    Endpoint de test pour l'API Stock
    """
    if request.method == 'GET':
        return Response({
            'message': 'API Stock fonctionne correctement !',
            'endpoints': [
                'GET /api/stock/movements/ - Lister les mouvements',
                'POST /api/stock/movements/ - Créer un mouvement',
                'GET /api/stock/adjustments/ - Lister les ajustements',
                'POST /api/stock/adjustments/ - Créer un ajustement',
                'GET /api/stock/alerts/ - Lister les alertes',
                'GET /api/stock/reports/ - Lister les rapports',
            ]
        })
    
    elif request.method == 'POST':
        return Response({
            'message': 'Test POST réussi !',
            'data': request.data
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def movements_summary(request):
    """
    Résumé des mouvements de stock pour le dashboard.
    """
    try:
        from apps.inventory.models import Product
        
        # Statistiques générales
        total_movements = StockMovement.objects.count()
        movements_in = StockMovement.objects.filter(movement_type='in').count()
        movements_out = StockMovement.objects.filter(movement_type='out').count()
        movements_adjustment = StockMovement.objects.filter(movement_type='adjustment').count()
        
        # Valeur totale du stock
        stock_movements_in = StockMovement.objects.filter(movement_type='in')
        total_stock_value = sum(
            movement.quantity * movement.unit_cost 
            for movement in stock_movements_in
        )
        
        # Nombre de produits
        products_count = Product.objects.count()
        
        # Alertes de stock
        low_stock_alerts = StockAlert.objects.filter(
            alert_type='low_stock',
            is_active=True
        ).count()
        
        out_of_stock_alerts = StockAlert.objects.filter(
            alert_type='out_of_stock',
            is_active=True
        ).count()
        
        # Produits en rupture
        out_of_stock_products = Product.objects.filter(
            stock_quantity__lte=0
        ).count()
        
        # Mouvements récents (7 derniers jours)
        week_ago = timezone.now().date() - timedelta(days=7)
        recent_movements = StockMovement.objects.filter(
            created_at__date__gte=week_ago
        ).count()
        
        # Valeur des mouvements récents
        recent_movements_value = StockMovement.objects.filter(
            created_at__date__gte=week_ago,
            movement_type='in'
        ).aggregate(
            total=Sum(F('quantity') * F('unit_cost'))
        )['total'] or Decimal('0.00')
        
        data = {
            "movements": {
                "total": total_movements,
                "in": movements_in,
                "out": movements_out,
                "adjustment": movements_adjustment,
                "recent": recent_movements
            },
            "stock": {
                "total_value": float(total_stock_value),
                "products_count": products_count,
                "out_of_stock": out_of_stock_products
            },
            "alerts": {
                "low_stock": low_stock_alerts,
                "out_of_stock": out_of_stock_alerts,
                "total": low_stock_alerts + out_of_stock_alerts
            },
            "recent_activity": {
                "movements_count": recent_movements,
                "value": float(recent_movements_value)
            }
        }
        
        return Response({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "MOVEMENTS_SUMMARY_ERROR",
                "message": "Erreur lors de la récupération du résumé des mouvements de stock",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)