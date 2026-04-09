#!/usr/bin/env python
"""
Script pour donner les permissions customers à l'utilisateur
"""
import os
import sys
import django

# Ajouter le répertoire du projet au path
sys.path.append('/Users/pc/nodus-erp/nodus')

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from django.contrib.auth.models import User
from apps.permissions.models import Permission, Role, RolePermission

def main():
    print("🔧 Attribution des permissions customers...")
    
    # Récupérer l'utilisateur
    try:
        user = User.objects.get(id=10)  # test_color_final
        print(f"✅ Utilisateur trouvé: {user.username}")
    except User.DoesNotExist:
        print("❌ Utilisateur non trouvé")
        return
    
    # Récupérer le rôle Admin
    try:
        admin_role = Role.objects.get(name='Admin')
        print(f"✅ Rôle Admin trouvé: {admin_role.name}")
    except Role.DoesNotExist:
        print("❌ Rôle Admin non trouvé")
        return
    
    # Permissions à créer/attribuer
    permissions_data = [
        {'name': 'customers_view', 'app_label': 'customers', 'resource': 'customers', 'action': 'view'},
        {'name': 'customers_create', 'app_label': 'customers', 'resource': 'customers', 'action': 'create'},
        {'name': 'customers_update', 'app_label': 'customers', 'resource': 'customers', 'action': 'update'},
        {'name': 'customers_delete', 'app_label': 'customers', 'resource': 'customers', 'action': 'delete'}
    ]
    
    for perm_data in permissions_data:
        # Créer ou récupérer la permission
        permission, created = Permission.objects.get_or_create(
            name=perm_data['name'],
            defaults={
                'app_label': perm_data['app_label'],
                'resource': perm_data['resource'],
                'action': perm_data['action']
            }
        )
        
        if created:
            print(f"✅ Permission créée: {perm_data['name']}")
        else:
            print(f"ℹ️  Permission existe déjà: {perm_data['name']}")
        
        # Lier la permission au rôle Admin
        role_perm, created = RolePermission.objects.get_or_create(
            role=admin_role,
            permission=permission
        )
        
        if created:
            print(f"✅ Permission {perm_data['name']} ajoutée au rôle Admin")
        else:
            print(f"ℹ️  Permission {perm_data['name']} déjà liée au rôle Admin")
    
    print("\n📋 Permissions du rôle Admin:")
    role_permissions = RolePermission.objects.filter(role=admin_role)
    for rp in role_permissions:
        print(f"  - {rp.permission.name}")
    
    print("\n✅ Script terminé!")

if __name__ == '__main__':
    main()
