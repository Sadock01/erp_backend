from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, Invoice, ProformaInvoice, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'variant', 'quantity', 'unit_price', 'discount_rate', 'total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer', 'status', 'order_date', 'total_amount', 'user', 'created_at'
    ]
    list_filter = ['status', 'order_date', 'created_at', 'updated_at']
    search_fields = ['order_number', 'customer__first_name', 'customer__last_name', 'notes']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'order_number']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('customer', 'order_number', 'status', 'order_date', 'delivery_date')
        }),
        ('Montants', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total_amount', 'discount_rate', 'discount_amount')
        }),
        ('Notes', {
            'fields': ('notes', 'internal_notes')
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'user'
        ).prefetch_related('items')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'product', 'variant', 'quantity', 'unit_price', 'total_price', 'created_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['order__order_number', 'product__name', 'variant__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'total_price']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('order', 'product', 'variant')
        }),
        ('Quantités et prix', {
            'fields': ('quantity', 'unit_price', 'discount_rate', 'discount_amount', 'total_price')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'product', 'variant'
        )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'order', 'status', 'invoice_date', 'due_date', 
        'total_amount', 'paid_amount', 'remaining_amount', 'user', 'created_at'
    ]
    list_filter = ['status', 'invoice_date', 'due_date', 'created_at', 'updated_at']
    search_fields = ['invoice_number', 'order__order_number', 'order__customer__first_name', 'order__customer__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'invoice_number']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('order', 'invoice_number', 'status', 'invoice_date', 'due_date')
        }),
        ('Montants', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total_amount', 'paid_amount', 'remaining_amount')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order__customer', 'user'
        )


@admin.register(ProformaInvoice)
class ProformaInvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'proforma_number', 'customer', 'status', 'proforma_date', 'valid_until', 
        'total_amount', 'user', 'created_at'
    ]
    list_filter = ['status', 'proforma_date', 'valid_until', 'created_at', 'updated_at']
    search_fields = ['proforma_number', 'customer__first_name', 'customer__last_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'proforma_number']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('customer', 'proforma_number', 'status', 'proforma_date', 'valid_until')
        }),
        ('Montants', {
            'fields': ('subtotal', 'tax_rate', 'tax_amount', 'total_amount')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'customer', 'user'
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'invoice', 'payment_method', 'amount', 'payment_date', 'reference', 'user', 'created_at'
    ]
    list_filter = ['payment_method', 'payment_date', 'created_at', 'updated_at']
    search_fields = ['invoice__invoice_number', 'reference', 'notes']
    ordering = ['-payment_date']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('invoice', 'payment_method', 'amount', 'payment_date')
        }),
        ('Références', {
            'fields': ('reference', 'notes')
        }),
        ('Utilisateur', {
            'fields': ('user',)
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'invoice__order__customer', 'user'
        )