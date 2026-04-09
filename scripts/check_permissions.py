#!/usr/bin/env python
"""
Script pour vérifier les permissions existantes dans la base de données
Usage: python check_permissions.py
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from apps.permissions.models import Permission, Role, UserRole
from django.contrib.auth.models import User

def check_permissions():
    """Vérifie les permissions existantes dans la base de données"""
    
    print("=" * 60)
    print("🔍 VÉRIFICATION DES PERMISSIONS - Baobab CRM-ERP")
    print("=" * 60)
    
    # 1. Vérifier le nombre total de permissions
    total_permissions = Permission.objects.count()
    print(f"\n📊 NOMBRE TOTAL DE PERMISSIONS: {total_permissions}")
    
    if total_permissions == 0:
        print("❌ AUCUNE PERMISSION TROUVÉE dans la base de données !")
        return
    
    # 2. Lister les permissions par application
    print(f"\n📋 PERMISSIONS PAR APPLICATION:")
    print("-" * 40)
    
    apps = Permission.objects.values_list('app_label', flat=True).distinct()
    for app in sorted(apps):
        app_permissions = Permission.objects.filter(app_label=app)
        print(f"\n🔹 {app.upper()} ({app_permissions.count()} permissions):")
        
        for perm in app_permissions:
            status = "✅" if perm.is_active else "❌"
            system = " [SYSTÈME]" if perm.is_system else ""
            print(f"   {status} {perm.codename} - {perm.name}{system}")
    
    # 3. Vérifier les permissions spécifiques pour customers
    print(f"\n🎯 PERMISSIONS CUSTOMERS (nécessaires pour la sécurisation):")
    print("-" * 50)
    
    customers_permissions = [
        ('customers.customer.view', 'Voir les clients'),
        ('customers.customer.create', 'Créer des clients'),
        ('customers.customer.update', 'Modifier des clients'),
        ('customers.customer.delete', 'Supprimer des clients'),
        ('customers.customer.manage', 'Gestion complète des clients'),
    ]
    
    for codename, name in customers_permissions:
        try:
            perm = Permission.objects.get(codename=codename)
            status = "✅" if perm.is_active else "❌"
            print(f"   {status} {codename} - {name}")
        except Permission.DoesNotExist:
            print(f"   ❌ {codename} - {name} (MANQUANTE)")
    
    # 4. Vérifier les rôles
    print(f"\n👥 RÔLES EXISTANTS:")
    print("-" * 30)
    
    total_roles = Role.objects.count()
    print(f"Nombre total de rôles: {total_roles}")
    
    if total_roles > 0:
        for role in Role.objects.all():
            user_count = role.user_count
            perm_count = role.permission_count
            status = "✅" if role.is_active else "❌"
            system = " [SYSTÈME]" if role.is_system else ""
            print(f"   {status} {role.name} (Niveau {role.level}) - {user_count} utilisateurs, {perm_count} permissions{system}")
    else:
        print("   ❌ AUCUN RÔLE TROUVÉ")
    
    # 5. Vérifier les assignations de rôles
    print(f"\n🔗 ASSIGNATIONS DE RÔLES:")
    print("-" * 35)
    
    total_assignments = UserRole.objects.count()
    print(f"Nombre total d'assignations: {total_assignments}")
    
    if total_assignments > 0:
        active_assignments = UserRole.objects.filter(is_active=True).count()
        expired_assignments = UserRole.objects.filter(expires_at__lt=django.utils.timezone.now()).count()
        print(f"   - Actives: {active_assignments}")
        print(f"   - Expirées: {expired_assignments}")
        
        print(f"\n   Détail des assignations:")
        for assignment in UserRole.objects.all()[:10]:  # Limiter à 10 pour l'affichage
            status = "✅" if assignment.is_active else "❌"
            expired = " [EXPIRÉ]" if assignment.is_expired else ""
            print(f"   {status} {assignment.user.username} → {assignment.role.name}{expired}")
        
        if total_assignments > 10:
            print(f"   ... et {total_assignments - 10} autres assignations")
    else:
        print("   ❌ AUCUNE ASSIGNATION TROUVÉE")
    
    # 6. Recommandations
    print(f"\n💡 RECOMMANDATIONS:")
    print("-" * 25)
    
    if total_permissions == 0:
        print("❌ CRÉER les permissions de base pour sécuriser les APIs")
    elif Permission.objects.filter(app_label='customers').count() == 0:
        print("❌ CRÉER les permissions customers pour sécuriser l'API customers")
    else:
        print("✅ Les permissions customers existent")
    
    if total_roles == 0:
        print("❌ CRÉER les rôles de base (Admin, Manager, Sales, etc.)")
    else:
        print("✅ Des rôles existent")
    
    if total_assignments == 0:
        print("❌ ASSIGNER des rôles aux utilisateurs")
    else:
        print("✅ Des assignations de rôles existent")
    
    print(f"\n" + "=" * 60)
    print("✅ Vérification terminée !")
    print("=" * 60)

if __name__ == "__main__":
    try:
        check_permissions()
    except Exception as e:
        print(f"❌ ERREUR lors de la vérification: {e}")
        sys.exit(1)
