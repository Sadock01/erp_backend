#!/usr/bin/env python
"""
Script de test simple pour l'API Analytics - Accès ouvert
"""
import os
import sys
import django
import requests

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def test_analytics_simple():
    """Test simple de l'API Analytics"""
    base_url = 'http://localhost:8000'
    
    # Récupérer le premier utilisateur disponible ou en créer un
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='testpass123'
            )
            print(f"✅ Utilisateur de test créé: {user.username}")
        else:
            print(f"🔄 Utilisateur existant: {user.username}")
        
        # Créer ou récupérer le token
        token, created = Token.objects.get_or_create(user=user)
        if created:
            print(f"✅ Token créé: {token.key}")
        else:
            print(f"🔄 Token existant: {token.key}")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        return
    
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🧪 Test simple de l'API Analytics...")
    print(f"🔑 Token: {token.key}")
    print(f"👤 Utilisateur: {user.username}")
    
    # Test de l'endpoint principal
    try:
        print(f"\n📊 Test: Analytics Principal")
        response = requests.get(
            f'{base_url}/api/analytics/',
            headers=headers,
            params={'period': '30d'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Succès (200)")
            print(f"   📄 Données reçues: {len(data)} sections")
            
            if 'kpis' in data:
                kpis = data['kpis']
                print(f"   💰 CA Total: {kpis.get('total_sales', 'N/A'):,} FCFA")
                print(f"   📈 Croissance: {kpis.get('sales_growth', 'N/A')}%")
            
            if 'top_customers' in data:
                customers = data['top_customers']
                print(f"   👥 Top clients: {len(customers)} clients")
            
            if 'top_products' in data:
                products = data['top_products']
                print(f"   📦 Top produits: {len(products)} produits")
            
            print(f"   🎉 L'API Analytics fonctionne parfaitement !")
            
        elif response.status_code == 403:
            print(f"   ❌ Accès refusé (403)")
            print(f"   🔒 L'API nécessite encore des permissions spéciales")
            
        else:
            print(f"   ❌ Erreur ({response.status_code})")
            print(f"   📄 Réponse: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Erreur de connexion")
        print(f"   💡 Démarrez le serveur avec: python manage.py runserver")
        
    except Exception as e:
        print(f"   ❌ Erreur: {str(e)}")


if __name__ == '__main__':
    print("🚀 Test simple de l'API Analytics")
    test_analytics_simple()
