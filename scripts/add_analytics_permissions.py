#!/usr/bin/env python
"""
Script pour ajouter les permissions Analytics
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from apps.permissions.models import Permission


def create_analytics_permissions():
    """Créer les permissions pour Analytics"""
    
    permissions_data = [
        {
            'name': 'Lire les analytics',
            'codename': 'analytics:read',
            'description': 'Accès en lecture aux données analytics et rapports',
            'app_label': 'analytics',
            'action': 'read',
            'resource': 'analytics',
            'is_active': True,
            'is_system': True
        },
        {
            'name': 'Gérer les analytics',
            'codename': 'analytics:manage',
            'description': 'Gestion complète des analytics et configuration des rapports',
            'app_label': 'analytics',
            'action': 'manage',
            'resource': 'analytics',
            'is_active': True,
            'is_system': True
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for perm_data in permissions_data:
        permission, created = Permission.objects.update_or_create(
            codename=perm_data['codename'],
            defaults=perm_data
        )
        
        if created:
            print(f"✅ Permission créée: {permission.name} ({permission.codename})")
            created_count += 1
        else:
            print(f"🔄 Permission mise à jour: {permission.name} ({permission.codename})")
            updated_count += 1
    
    print(f"\n📊 Résumé:")
    print(f"   - Permissions créées: {created_count}")
    print(f"   - Permissions mises à jour: {updated_count}")
    print(f"   - Total: {created_count + updated_count}")


if __name__ == '__main__':
    print("🚀 Ajout des permissions Analytics...")
    create_analytics_permissions()
    print("✅ Permissions Analytics ajoutées avec succès!")
