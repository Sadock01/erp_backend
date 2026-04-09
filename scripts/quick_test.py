#!/usr/bin/env python3
"""
Script de test rapide pour vérifier les APIs Dashboard
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from apps.dashboard.views import *

def test_dashboard_apis():
    """Test rapide des APIs dashboard"""
    print("🧪 Test rapide des APIs Dashboard")
    print("=" * 40)
    
    # Créer un client de test
    client = Client()
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Utilisateur de test créé")
    
    # Se connecter
    login_success = client.login(username='testuser', password='testpass123')
    if not login_success:
        print("❌ Échec de la connexion")
        return
    
    print("✅ Connexion réussie")
    
    # Tester les endpoints
    endpoints = [
        ('/api/dashboard/kpis/', 'KPIs'),
        ('/api/dashboard/sales-chart/', 'Graphique des ventes'),
        ('/api/dashboard/products-chart/', 'Top produits'),
        ('/api/dashboard/clients-chart/', 'Répartition clients'),
        ('/api/dashboard/alerts/', 'Alertes'),
        ('/api/dashboard/recent-orders/', 'Commandes récentes'),
        ('/api/dashboard/recent-invoices/', 'Factures récentes'),
        ('/api/dashboard/', 'Dashboard complet'),
    ]
    
    for endpoint, name in endpoints:
        response = client.get(endpoint)
        if response.status_code == 200:
            print(f"✅ {name}: OK")
        else:
            print(f"❌ {name}: Erreur {response.status_code}")
            if response.status_code == 500:
                print(f"   Détails: {response.content.decode()[:200]}...")
    
    print("\n🎉 Test terminé !")

if __name__ == "__main__":
    test_dashboard_apis()
