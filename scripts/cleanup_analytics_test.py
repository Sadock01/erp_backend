#!/usr/bin/env python
"""
Script de nettoyage pour supprimer les données de test Analytics
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from apps.permissions.models import Role, UserRole, RolePermission
from apps.analytics.models import AnalyticsCache


def cleanup_analytics_test_data():
    """Nettoyer les données de test Analytics"""
    
    print("🧹 Nettoyage des données de test Analytics...")
    
    # Supprimer l'utilisateur de test
    try:
        user = User.objects.get(username='analytics_test')
        user.delete()
        print("✅ Utilisateur de test supprimé")
    except User.DoesNotExist:
        print("ℹ️  Utilisateur de test non trouvé")
    
    # Supprimer le rôle de test
    try:
        role = Role.objects.get(name='Analytics Manager')
        role.delete()
        print("✅ Rôle de test supprimé")
    except Role.DoesNotExist:
        print("ℹ️  Rôle de test non trouvé")
    
    # Supprimer le cache Analytics
    cache_count = AnalyticsCache.objects.count()
    if cache_count > 0:
        AnalyticsCache.objects.all().delete()
        print(f"✅ Cache Analytics supprimé ({cache_count} entrées)")
    else:
        print("ℹ️  Aucun cache Analytics trouvé")
    
    print("🎯 Nettoyage terminé!")


if __name__ == '__main__':
    cleanup_analytics_test_data()
