from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Role, Permission, RolePermission, UserRole, PermissionLog


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'user_count', 'permission_count', 'is_active', 'is_system', 'created_at']
    list_filter = ['is_active', 'is_system', 'level', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['level', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'description', 'level')
        }),
        ('Apparence', {
            'fields': ('color', 'icon'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active', 'is_system')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def user_count(self, obj):
        count = obj.user_count
        if count > 0:
            url = reverse('admin:permissions_userrole_changelist') + f'?role__id__exact={obj.id}'
            return format_html('<a href="{}">{} utilisateur(s)</a>', url, count)
        return '0 utilisateur'
    user_count.short_description = 'Utilisateurs'
    
    def permission_count(self, obj):
        count = obj.permission_count
        if count > 0:
            url = reverse('admin:permissions_rolepermission_changelist') + f'?role__id__exact={obj.id}'
            return format_html('<a href="{}">{} permission(s)</a>', url, count)
        return '0 permission'
    permission_count.short_description = 'Permissions'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'app_label', 'resource', 'action', 'is_active', 'is_system', 'created_at']
    list_filter = ['is_active', 'is_system', 'app_label', 'action', 'resource', 'created_at']
    search_fields = ['name', 'codename', 'description']
    ordering = ['app_label', 'resource', 'action']
    readonly_fields = ['created_at', 'updated_at', 'full_codename']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('name', 'codename', 'description')
        }),
        ('Classification', {
            'fields': ('app_label', 'resource', 'action', 'full_codename')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_system')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 0
    fields = ['permission', 'granted', 'conditions', 'notes']
    autocomplete_fields = ['permission']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ['role', 'permission', 'granted', 'created_at']
    list_filter = ['granted', 'role', 'permission__app_label', 'created_at']
    search_fields = ['role__name', 'permission__name', 'permission__codename']
    ordering = ['role', 'permission']
    readonly_fields = ['created_at', 'updated_at']
    autocomplete_fields = ['role', 'permission']
    
    fieldsets = (
        ('Attribution', {
            'fields': ('role', 'permission', 'granted')
        }),
        ('Conditions', {
            'fields': ('conditions', 'notes'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'assigned_by', 'is_active', 'is_expired', 'assigned_at', 'expires_at']
    list_filter = ['is_active', 'role', 'assigned_by', 'assigned_at', 'expires_at']
    search_fields = ['user__username', 'user__email', 'role__name', 'assigned_by__username']
    ordering = ['-assigned_at']
    readonly_fields = ['assigned_at', 'created_at', 'updated_at', 'is_expired', 'days_until_expiry']
    autocomplete_fields = ['user', 'role', 'assigned_by']
    
    fieldsets = (
        ('Assignation', {
            'fields': ('user', 'role', 'assigned_by')
        }),
        ('Durée', {
            'fields': ('expires_at', 'is_expired', 'days_until_expiry')
        }),
        ('Statut', {
            'fields': ('is_active', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('assigned_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def is_expired(self, obj):
        if obj.is_expired:
            return format_html('<span style="color: red;">✓ Expiré</span>')
        return format_html('<span style="color: green;">✗ Actif</span>')
    is_expired.short_description = 'Expiré'
    
    def days_until_expiry(self, obj):
        days = obj.days_until_expiry
        if days is None:
            return 'Permanent'
        elif days < 0:
            return format_html('<span style="color: red;">{} jours en retard</span>', abs(days))
        elif days <= 7:
            return format_html('<span style="color: orange;">{} jours</span>', days)
        else:
            return f'{days} jours'
    days_until_expiry.short_description = 'Jours restants'


@admin.register(PermissionLog)
class PermissionLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'target_user', 'role', 'permission', 'created_at']
    list_filter = ['action', 'created_at', 'user', 'target_user', 'role']
    search_fields = ['user__username', 'target_user__username', 'role__name', 'permission__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Action', {
            'fields': ('action', 'user', 'target_user')
        }),
        ('Contexte', {
            'fields': ('role', 'permission', 'details')
        }),
        ('Informations techniques', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Personnalisation de l'interface d'administration
admin.site.site_header = "Baobab CRM-ERP - Administration des Permissions"
admin.site.site_title = "Administration Permissions"
admin.site.index_title = "Gestion des Rôles et Permissions"