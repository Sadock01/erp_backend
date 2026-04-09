#!/usr/bin/env python3
"""
Script pour lister toutes les APIs disponibles
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from django.urls import get_resolver

def list_all_apis():
    """Lister toutes les APIs disponibles"""
    print("📋 APIs Disponibles - Baobab ERP")
    print("=" * 50)
    
    resolver = get_resolver()
    
    def extract_urls(urlpatterns, prefix=''):
        """Extraire toutes les URLs"""
        urls = []
        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                # C'est un include
                urls.extend(extract_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            else:
                # C'est une URL
                url = prefix + str(pattern.pattern)
                if hasattr(pattern, 'name') and pattern.name:
                    urls.append((url, pattern.name, pattern.callback.__name__ if hasattr(pattern, 'callback') else 'N/A'))
        return urls
    
    all_urls = extract_urls(resolver.url_patterns)
    
    # Grouper par module
    modules = {}
    for url, name, callback in all_urls:
        if url.startswith('/api/'):
            module = url.split('/')[2] if len(url.split('/')) > 2 else 'root'
            if module not in modules:
                modules[module] = []
            modules[module].append((url, name, callback))
    
    # Afficher par module
    for module, urls in modules.items():
        print(f"\n🔹 Module: {module.upper()}")
        print("-" * 30)
        for url, name, callback in sorted(urls):
            method = "GET/POST/PUT/DELETE"  # Par défaut pour les ViewSets
            if 'dashboard' in url:
                method = "GET"
            elif 'auth' in url:
                method = "POST" if 'login' in url else "GET"
            
            print(f"  {method:15} {url:30} ({name})")
    
    print(f"\n📊 Total: {len(all_urls)} endpoints")
    
    # APIs Dashboard spécifiques
    print(f"\n🎯 APIs Dashboard Principales:")
    print("-" * 30)
    dashboard_apis = [
        ("GET", "/api/dashboard/", "Dashboard complet"),
        ("GET", "/api/dashboard/kpis/", "KPIs principaux"),
        ("GET", "/api/dashboard/sales-chart/", "Graphique des ventes"),
        ("GET", "/api/dashboard/products-chart/", "Top produits"),
        ("GET", "/api/dashboard/clients-chart/", "Répartition clients"),
        ("GET", "/api/dashboard/alerts/", "Alertes"),
        ("GET", "/api/dashboard/recent-orders/", "Commandes récentes"),
        ("GET", "/api/dashboard/recent-invoices/", "Factures récentes"),
    ]
    
    for method, url, description in dashboard_apis:
        print(f"  {method:15} {url:30} {description}")
    
    print(f"\n📋 APIs de Résumé:")
    print("-" * 30)
    summary_apis = [
        ("GET", "/api/sales/orders/summary/", "Résumé des commandes"),
        ("GET", "/api/sales/invoices/summary/", "Résumé des factures"),
        ("GET", "/api/stock/movements/summary/", "Résumé du stock"),
    ]
    
    for method, url, description in summary_apis:
        print(f"  {method:15} {url:30} {description}")
    
    print(f"\n🔐 Authentification requise pour toutes les APIs")
    print(f"   Header: Authorization: Token <votre_token>")
    print(f"   Obtenir un token: POST /api/auth/login/")

if __name__ == "__main__":
    list_all_apis()
