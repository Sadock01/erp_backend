#!/usr/bin/env python3
"""
Script pour configurer les permissions dans Baobab ERP
- Donne toutes les permissions à tous les utilisateurs existants
- Configure l'inscription pour que les nouveaux utilisateurs soient admin
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from apps.permissions.models import Role, Permission, UserRole, RolePermission
from django.db import transaction
from django.utils import timezone

def create_admin_role():
    """Crée le rôle Admin avec toutes les permissions"""
    print("🔧 Création du rôle Admin...")
    
    admin_role, created = Role.objects.get_or_create(
        name="Admin",
        defaults={
            'description': "Administrateur avec toutes les permissions",
            'is_active': True,
            'is_system': True,
            'level': 0,  # Niveau le plus élevé
            'color': "#dc3545",  # Rouge pour admin
            'icon': "fas fa-user-shield"
        }
    )
    
    if created:
        print(f"✅ Rôle Admin créé avec l'ID: {admin_role.id}")
    else:
        print(f"✅ Rôle Admin existe déjà avec l'ID: {admin_role.id}")
    
    return admin_role

def create_all_permissions():
    """Crée toutes les permissions nécessaires"""
    print("🔧 Création des permissions...")
    
    # Liste de toutes les permissions nécessaires
    permissions_data = [
        # Permissions générales
        ('Voir le tableau de bord', 'dashboard_view', 'dashboard', 'view', 'dashboard'),
        ('Gérer le tableau de bord', 'dashboard_manage', 'dashboard', 'manage', 'dashboard'),
        
        # Permissions inventaire
        ('Voir les produits', 'inventory_view', 'inventory', 'view', 'product'),
        ('Créer des produits', 'inventory_create', 'inventory', 'create', 'product'),
        ('Modifier des produits', 'inventory_update', 'inventory', 'update', 'product'),
        ('Supprimer des produits', 'inventory_delete', 'inventory', 'delete', 'product'),
        ('Gérer les produits', 'inventory_manage', 'inventory', 'manage', 'product'),
        
        # Permissions catégories
        ('Voir les catégories', 'inventory_category.view', 'inventory', 'view', 'category'),
        ('Créer des catégories', 'inventory_category.create', 'inventory', 'create', 'category'),
        ('Modifier des catégories', 'inventory_category.update', 'inventory', 'update', 'category'),
        ('Supprimer des catégories', 'inventory_category.delete', 'inventory', 'delete', 'category'),
        ('Gérer les catégories', 'inventory_category.manage', 'inventory', 'manage', 'category'),
        
        # Permissions variants
        ('Voir les variants', 'inventory_variant.view', 'inventory', 'view', 'variant'),
        ('Créer des variants', 'inventory_variant.create', 'inventory', 'create', 'variant'),
        ('Modifier des variants', 'inventory_variant.update', 'inventory', 'update', 'variant'),
        ('Supprimer des variants', 'inventory_variant.delete', 'inventory', 'delete', 'variant'),
        ('Gérer les variants', 'inventory_variant.manage', 'inventory', 'manage', 'variant'),
        
        # Permissions stock
        ('Voir le stock', 'stock_view', 'stock', 'view', 'stock'),
        ('Gérer le stock', 'stock_manage', 'stock', 'manage', 'stock'),
        ('Ajuster le stock', 'stock_adjust', 'stock', 'adjust', 'stock'),
        
        # Permissions ventes
        ('Voir les commandes', 'sales_order.view', 'sales', 'view', 'order'),
        ('Créer des commandes', 'sales_order.create', 'sales', 'create', 'order'),
        ('Modifier des commandes', 'sales_order.update', 'sales', 'update', 'order'),
        ('Supprimer des commandes', 'sales_order.delete', 'sales', 'delete', 'order'),
        ('Gérer les commandes', 'sales_order.manage', 'sales', 'manage', 'order'),
        
        # Permissions factures
        ('Voir les factures', 'sales_invoice.view', 'sales', 'view', 'invoice'),
        ('Créer des factures', 'sales_invoice.create', 'sales', 'create', 'invoice'),
        ('Modifier des factures', 'sales_invoice.update', 'sales', 'update', 'invoice'),
        ('Supprimer des factures', 'sales_invoice.delete', 'sales', 'delete', 'invoice'),
        ('Gérer les factures', 'sales_invoice.manage', 'sales', 'manage', 'invoice'),
        
        # Permissions clients
        ('Voir les clients', 'customers_view', 'customers', 'view', 'customer'),
        ('Créer des clients', 'customers_create', 'customers', 'create', 'customer'),
        ('Modifier des clients', 'customers_update', 'customers', 'update', 'customer'),
        ('Supprimer des clients', 'customers_delete', 'customers', 'delete', 'customer'),
        ('Gérer les clients', 'customers_manage', 'customers', 'manage', 'customer'),
        
        # Permissions alertes
        ('Voir les alertes', 'alerts_view', 'alerts', 'view', 'alert'),
        ('Créer des alertes', 'alerts_create', 'alerts', 'create', 'alert'),
        ('Modifier des alertes', 'alerts_update', 'alerts', 'update', 'alert'),
        ('Supprimer des alertes', 'alerts_delete', 'alerts', 'delete', 'alert'),
        ('Gérer les alertes', 'alerts_manage', 'alerts', 'manage', 'alert'),
        
        # Permissions notifications
        ('Voir les notifications', 'notifications_view', 'notifications', 'view', 'notification'),
        ('Créer des notifications', 'notifications_create', 'notifications', 'create', 'notification'),
        ('Modifier des notifications', 'notifications_update', 'notifications', 'update', 'notification'),
        ('Supprimer des notifications', 'notifications_delete', 'notifications', 'delete', 'notification'),
        ('Gérer les notifications', 'notifications_manage', 'notifications', 'manage', 'notification'),
        
        # Permissions utilisateurs
        ('Voir les utilisateurs', 'users_view', 'users', 'view', 'user'),
        ('Créer des utilisateurs', 'users_create', 'users', 'create', 'user'),
        ('Modifier des utilisateurs', 'users_update', 'users', 'update', 'user'),
        ('Supprimer des utilisateurs', 'users_delete', 'users', 'delete', 'user'),
        ('Gérer les utilisateurs', 'users_manage', 'users', 'manage', 'user'),
        
        # Permissions rôles
        ('Voir les rôles', 'roles_view', 'roles', 'view', 'role'),
        ('Créer des rôles', 'roles_create', 'roles', 'create', 'role'),
        ('Modifier des rôles', 'roles_update', 'roles', 'update', 'role'),
        ('Supprimer des rôles', 'roles_delete', 'roles', 'delete', 'role'),
        ('Gérer les rôles', 'roles_manage', 'roles', 'manage', 'role'),
        
        # Permissions permissions
        ('Voir les permissions', 'permissions_view', 'permissions', 'view', 'permission'),
        ('Créer des permissions', 'permissions_create', 'permissions', 'create', 'permission'),
        ('Modifier des permissions', 'permissions_update', 'permissions', 'update', 'permission'),
        ('Supprimer des permissions', 'permissions_delete', 'permissions', 'delete', 'permission'),
        ('Gérer les permissions', 'permissions_manage', 'permissions', 'manage', 'permission'),
    ]
    
    created_count = 0
    for name, codename, app_label, action, resource in permissions_data:
        permission, created = Permission.objects.get_or_create(
            codename=codename,
            defaults={
                'name': name,
                'description': f"Permission pour {action} {resource} dans {app_label}",
                'app_label': app_label,
                'action': action,
                'resource': resource,
                'is_active': True,
                'is_system': True
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ {created_count} nouvelles permissions créées")
    print(f"✅ Total des permissions: {Permission.objects.count()}")
    
    return Permission.objects.all()

def assign_all_permissions_to_admin_role(admin_role, permissions):
    """Assigne toutes les permissions au rôle Admin"""
    print("🔧 Attribution de toutes les permissions au rôle Admin...")
    
    created_count = 0
    for permission in permissions:
        role_permission, created = RolePermission.objects.get_or_create(
            role=admin_role,
            permission=permission,
            defaults={
                'granted': True,
                'notes': 'Attribué automatiquement lors de la configuration'
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ {created_count} permissions attribuées au rôle Admin")
    print(f"✅ Total des permissions du rôle Admin: {RolePermission.objects.filter(role=admin_role, granted=True).count()}")

def assign_admin_role_to_all_users(admin_role):
    """Assigne le rôle Admin à tous les utilisateurs existants"""
    print("🔧 Attribution du rôle Admin à tous les utilisateurs...")
    
    users = User.objects.all()
    created_count = 0
    
    for user in users:
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=admin_role,
            defaults={
                'is_active': True,
                'assigned_at': timezone.now(),
                'notes': 'Attribué automatiquement lors de la configuration'
            }
        )
        if created:
            created_count += 1
    
    print(f"✅ Rôle Admin attribué à {created_count} utilisateurs")
    print(f"✅ Total des utilisateurs avec rôle Admin: {UserRole.objects.filter(role=admin_role, is_active=True).count()}")

def modify_register_view():
    """Modifie la vue d'inscription pour attribuer automatiquement le rôle Admin"""
    print("🔧 Modification de la vue d'inscription...")
    
    # Lire le fichier views.py
    views_file = 'apps/common/views.py'
    
    try:
        with open(views_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si la modification a déjà été faite
        if 'admin_role = Role.objects.get(name="Admin")' in content:
            print("✅ La vue d'inscription a déjà été modifiée")
            return
        
        # Trouver la fonction register et la modifier
        old_register = '''@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        return Response({
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''
        
        new_register = '''@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur avec attribution automatique du rôle Admin
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        
        # Attribuer automatiquement le rôle Admin
        try:
            from apps.permissions.models import Role, UserRole
            admin_role = Role.objects.get(name="Admin")
            UserRole.objects.create(
                user=user,
                role=admin_role,
                is_active=True,
                notes='Attribué automatiquement lors de l\'inscription'
            )
        except Exception as e:
            print(f"Erreur lors de l'attribution du rôle Admin: {e}")
        
        return Response({
            'success': True,
            'message': 'Utilisateur créé avec succès et rôle Admin attribué',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''
        
        # Remplacer la fonction
        if old_register in content:
            content = content.replace(old_register, new_register)
            
            # Écrire le fichier modifié
            with open(views_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Vue d'inscription modifiée avec succès")
        else:
            print("⚠️  Impossible de trouver la fonction register à modifier")
            print("   Vous devrez modifier manuellement la vue d'inscription")
    
    except Exception as e:
        print(f"❌ Erreur lors de la modification de la vue d'inscription: {e}")

def main():
    """Fonction principale"""
    print("🚀 Configuration des permissions Baobab ERP")
    print("=" * 50)
    
    try:
        with transaction.atomic():
            # 1. Créer le rôle Admin
            admin_role = create_admin_role()
            
            # 2. Créer toutes les permissions
            permissions = create_all_permissions()
            
            # 3. Attribuer toutes les permissions au rôle Admin
            assign_all_permissions_to_admin_role(admin_role, permissions)
            
            # 4. Attribuer le rôle Admin à tous les utilisateurs existants
            assign_admin_role_to_all_users(admin_role)
            
            # 5. Modifier la vue d'inscription
            modify_register_view()
        
        print("\n" + "=" * 50)
        print("🎉 Configuration terminée avec succès!")
        print("\n📊 Résumé:")
        print(f"   - Utilisateurs: {User.objects.count()}")
        print(f"   - Rôles: {Role.objects.count()}")
        print(f"   - Permissions: {Permission.objects.count()}")
        print(f"   - Utilisateurs avec rôle Admin: {UserRole.objects.filter(role__name='Admin', is_active=True).count()}")
        print(f"   - Permissions du rôle Admin: {RolePermission.objects.filter(role__name='Admin', granted=True).count()}")
        
        print("\n✅ Tous les utilisateurs existants ont maintenant toutes les permissions")
        print("✅ Les nouveaux utilisateurs seront automatiquement admin")
        print("✅ Vous pouvez maintenant accéder à toutes les APIs sans restriction")
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
