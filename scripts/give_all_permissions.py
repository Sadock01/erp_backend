#!/usr/bin/env python
"""
Script pour donner toutes les permissions existantes à tous les utilisateurs existants
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from django.contrib.auth.models import User
from apps.permissions.models import Permission, Role, RolePermission, UserRole

def give_all_permissions_to_all_users():
    """
    Donne toutes les permissions existantes à tous les utilisateurs existants
    """
    print("🚀 Attribution de toutes les permissions à tous les utilisateurs")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs
    users = User.objects.all()
    print(f"👥 Nombre d'utilisateurs trouvés: {users.count()}")
    
    # Récupérer toutes les permissions
    all_permissions = Permission.objects.all()
    print(f"🔑 Nombre de permissions trouvées: {all_permissions.count()}")
    
    # Récupérer ou créer le rôle Admin
    admin_role, created = Role.objects.get_or_create(
        name='Admin',
        defaults={
            'description': 'Administrateur avec toutes les permissions',
            'level': 0
        }
    )
    
    if created:
        print("✅ Rôle Admin créé")
    else:
        print("✅ Rôle Admin existe déjà")
    
    # Donner toutes les permissions au rôle Admin (granted=True, y compris si la ligne existait avec granted=False)
    permissions_added = 0
    for permission in all_permissions:
        _, created = RolePermission.objects.update_or_create(
            role=admin_role,
            permission=permission,
            defaults={'granted': True},
        )
        if created:
            permissions_added += 1

    print(f"🔗 {permissions_added} nouvelles liaisons RolePermission créées pour le rôle Admin")
    print(
        f"📊 Total accordé (granted=True): "
        f"{RolePermission.objects.filter(role=admin_role, granted=True).count()}"
    )
    
    # Donner le rôle Admin à tous les utilisateurs (réactiver is_active si besoin)
    users_updated = 0
    for user in users:
        _, created = UserRole.objects.update_or_create(
            user=user,
            role=admin_role,
            defaults={'is_active': True},
        )
        if created:
            users_updated += 1

    print(f"👤 {users_updated} nouveaux UserRole Admin créés")
    print(f"📊 Total des utilisateurs avec rôle Admin: {UserRole.objects.filter(role=admin_role).count()}")
    
    print("\n" + "=" * 60)
    print("🎉 TERMINÉ!")
    print("✅ Tous les utilisateurs ont maintenant toutes les permissions")
    
    # Vérification finale
    print("\n🔍 VÉRIFICATION FINALE:")
    for user in users[:3]:  # Afficher les 3 premiers utilisateurs
        user_permissions = RolePermission.objects.filter(
            role__userrole__user=user
        ).count()
        print(f"   - {user.username}: {user_permissions} permissions")

if __name__ == "__main__":
    give_all_permissions_to_all_users()
