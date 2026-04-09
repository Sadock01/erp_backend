from django.contrib import admin
from django.utils.html import format_html
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """
    Configuration Django Admin pour les clients
    """
    list_display = [
        'full_name',
        'email',
        'phone',
        'company',
        'country',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active',
        'country',
        'created_at',
        'updated_at'
    ]
    search_fields = [
        'first_name',
        'last_name',
        'email',
        'phone',
        'company'
    ]
    ordering = ['last_name', 'first_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Informations professionnelles', {
            'fields': ('company',),
            'classes': ('collapse',)
        }),
        ('Adresse', {
            'fields': ('address', 'city', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Statut et notes', {
            'fields': ('is_active', 'notes'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        """Affiche le nom complet avec couleur selon le statut"""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">{}</span>',
                f"{obj.first_name} {obj.last_name}"
            )
        else:
            return format_html(
                '<span style="color: red;">{}</span>',
                f"{obj.first_name} {obj.last_name}"
            )
    full_name.short_description = 'Nom complet'
    full_name.admin_order_field = 'last_name'
    
    actions = ['activate_customers', 'deactivate_customers']
    
    def activate_customers(self, request, queryset):
        """Action pour activer plusieurs clients"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} client(s) activé(s) avec succès.'
        )
    activate_customers.short_description = "Activer les clients sélectionnés"
    
    def deactivate_customers(self, request, queryset):
        """Action pour désactiver plusieurs clients"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} client(s) désactivé(s) avec succès.'
        )
    deactivate_customers.short_description = "Désactiver les clients sélectionnés"
