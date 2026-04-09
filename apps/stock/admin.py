from django.contrib import admin
from django.utils.html import format_html
from .models import StockMovement, StockAdjustment, StockAlert, StockReport


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'variant', 'movement_type', 'quantity', 
        'unit_cost', 'total_cost', 'reference', 'user', 
        'is_approved', 'created_at'
    ]
    list_filter = [
        'movement_type', 'is_approved', 'created_at', 'updated_at'
    ]
    search_fields = [
        'product__name', 'variant__name', 'reference', 'notes', 'user__username'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'total_cost']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('product', 'variant', 'movement_type', 'quantity')
        }),
        ('Coûts', {
            'fields': ('unit_cost', 'total_cost')
        }),
        ('Références', {
            'fields': ('reference', 'notes')
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Approbation', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'variant', 'user', 'approved_by'
        )


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'variant', 'adjustment_type', 'quantity_before',
        'quantity_after', 'adjustment_quantity', 'user', 'is_approved', 'created_at'
    ]
    list_filter = [
        'adjustment_type', 'is_approved', 'created_at', 'updated_at'
    ]
    search_fields = [
        'product__name', 'variant__name', 'reason', 'user__username'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'adjustment_quantity']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('product', 'variant', 'adjustment_type')
        }),
        ('Quantités', {
            'fields': ('quantity_before', 'quantity_after', 'adjustment_quantity')
        }),
        ('Raison', {
            'fields': ('reason',)
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Approbation', {
            'fields': ('is_approved', 'approved_by', 'approved_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'variant', 'user', 'approved_by'
        )


@admin.register(StockAlert)
class StockAlertAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'variant', 'alert_type', 'current_quantity',
        'threshold_quantity', 'is_active', 'is_resolved', 'created_at'
    ]
    list_filter = [
        'alert_type', 'is_active', 'is_resolved', 'created_at', 'updated_at'
    ]
    search_fields = [
        'product__name', 'variant__name'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('product', 'variant', 'alert_type')
        }),
        ('Quantités', {
            'fields': ('current_quantity', 'threshold_quantity')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_resolved')
        }),
        ('Résolution', {
            'fields': ('resolved_by', 'resolved_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product', 'variant', 'resolved_by'
        )


@admin.register(StockReport)
class StockReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type', 'date_from', 'date_to',
        'user', 'is_generated', 'generated_at', 'created_at'
    ]
    list_filter = [
        'report_type', 'is_generated', 'created_at', 'generated_at'
    ]
    search_fields = [
        'title', 'description', 'user__username'
    ]
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'period_days']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'report_type')
        }),
        ('Période', {
            'fields': ('date_from', 'date_to', 'period_days')
        }),
        ('Filtres et données', {
            'fields': ('filters', 'data')
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Génération', {
            'fields': ('is_generated', 'generated_at')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')