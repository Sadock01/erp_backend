#!/usr/bin/env python
"""
Script pour vider le cache Analytics
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from apps.analytics.models import AnalyticsCache


def clear_analytics_cache():
    """Vider le cache Analytics"""
    print("🧹 Nettoyage du cache Analytics...")
    
    # Compter les entrées de cache
    cache_count = AnalyticsCache.objects.count()
    print(f"📊 Entrées de cache trouvées: {cache_count}")
    
    if cache_count > 0:
        # Supprimer tout le cache
        AnalyticsCache.objects.all().delete()
        print(f"✅ Cache vidé: {cache_count} entrées supprimées")
    else:
        print("ℹ️  Aucun cache à vider")
    
    print("🎯 Nettoyage terminé!")


if __name__ == '__main__':
    clear_analytics_cache()

