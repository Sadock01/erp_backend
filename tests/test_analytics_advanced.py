#!/usr/bin/env python
"""
Script de test avancé pour l'API Analytics avec différents paramètres
"""
import os
import sys
import django
import requests
import json

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def test_analytics_parameters():
    """Tester l'API Analytics avec différents paramètres"""
    base_url = 'http://localhost:8000'
    
    # Récupérer l'utilisateur de test
    try:
        user = User.objects.get(username='analytics_test')
        token = Token.objects.get(user=user)
        print(f"🔑 Token: {token.key}")
        print(f"👤 Utilisateur: {user.username}")
    except:
        print("❌ Utilisateur de test non trouvé. Exécutez d'abord test_analytics_api.py")
        return
    
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }
    
    # Tests avec différents paramètres
    test_cases = [
        {
            'name': 'Période 7 jours',
            'params': {'period': '7d'}
        },
        {
            'name': 'Période 90 jours',
            'params': {'period': '90d'}
        },
        {
            'name': 'Période 1 an',
            'params': {'period': '1y'}
        },
        {
            'name': 'Période personnalisée',
            'params': {
                'period': 'custom',
                'custom_start_date': '2024-01-01',
                'custom_end_date': '2024-01-31'
            }
        },
        {
            'name': 'Clients VIP',
            'params': {
                'period': '30d',
                'customer_segment': 'vip'
            }
        },
        {
            'name': 'Catégorie Électronique',
            'params': {
                'period': '30d',
                'product_category': 'electronics'
            }
        },
        {
            'name': 'Filtres combinés',
            'params': {
                'period': '30d',
                'customer_segment': 'returning',
                'product_category': 'electronics',
                'revenue_min': 1000000,
                'revenue_max': 5000000
            }
        }
    ]
    
    print(f"\n🧪 Test des paramètres Analytics...")
    
    for test_case in test_cases:
        try:
            print(f"\n📊 Test: {test_case['name']}")
            print(f"   Paramètres: {test_case['params']}")
            
            response = requests.get(
                f'{base_url}/api/analytics/',
                headers=headers,
                params=test_case['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès (200)")
                
                # Vérifier la structure des données
                if 'kpis' in data:
                    kpis = data['kpis']
                    print(f"   💰 CA Total: {kpis.get('total_sales', 'N/A'):,} FCFA")
                    print(f"   📈 Croissance: {kpis.get('sales_growth', 'N/A')}%")
                    print(f"   🛒 Panier moyen: {kpis.get('avg_order_value', 'N/A'):,} FCFA")
                
                if 'top_customers' in data:
                    customers = data['top_customers']
                    print(f"   👥 Top clients: {len(customers)} clients")
                    if customers:
                        top_customer = customers[0]
                        print(f"   🏆 Meilleur client: {top_customer.get('name', 'N/A')} ({top_customer.get('total_spent', 0):,} FCFA)")
                
                if 'top_products' in data:
                    products = data['top_products']
                    print(f"   📦 Top produits: {len(products)} produits")
                    if products:
                        top_product = products[0]
                        print(f"   🏆 Meilleur produit: {top_product.get('name', 'N/A')} ({top_product.get('sales', 0):,} FCFA)")
                
            elif response.status_code == 400:
                print(f"   ⚠️  Paramètres invalides (400)")
                try:
                    error_data = response.json()
                    print(f"   📄 Erreur: {error_data.get('error', {}).get('message', 'N/A')}")
                except:
                    print(f"   📄 Réponse: {response.text[:200]}...")
                    
            else:
                print(f"   ❌ Erreur ({response.status_code})")
                try:
                    error_data = response.json()
                    print(f"   📄 Erreur: {error_data}")
                except:
                    print(f"   📄 Réponse: {response.text[:200]}...")
                    
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erreur de connexion - Le serveur n'est pas démarré")
            print(f"   💡 Démarrez le serveur avec: python manage.py runserver")
            break
            
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
    
    print(f"\n🎯 Test des paramètres terminé!")


def test_error_cases():
    """Tester les cas d'erreur"""
    base_url = 'http://localhost:8000'
    
    try:
        user = User.objects.get(username='analytics_test')
        token = Token.objects.get(user=user)
    except:
        print("❌ Utilisateur de test non trouvé")
        return
    
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }
    
    error_cases = [
        {
            'name': 'Période invalide',
            'params': {'period': 'invalid'}
        },
        {
            'name': 'Période custom sans dates',
            'params': {'period': 'custom'}
        },
        {
            'name': 'Date de début invalide',
            'params': {
                'period': 'custom',
                'custom_start_date': 'invalid-date',
                'custom_end_date': '2024-01-31'
            }
        }
    ]
    
    print(f"\n🚨 Test des cas d'erreur...")
    
    for error_case in error_cases:
        try:
            print(f"\n❌ Test: {error_case['name']}")
            print(f"   Paramètres: {error_case['params']}")
            
            response = requests.get(
                f'{base_url}/api/analytics/',
                headers=headers,
                params=error_case['params'],
                timeout=10
            )
            
            if response.status_code == 400:
                print(f"   ✅ Erreur attendue (400)")
                try:
                    error_data = response.json()
                    print(f"   📄 Message: {error_data.get('error', {}).get('message', 'N/A')}")
                except:
                    print(f"   📄 Réponse: {response.text[:200]}...")
            else:
                print(f"   ⚠️  Code inattendu ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Erreur: {str(e)}")
    
    print(f"\n🎯 Test des erreurs terminé!")


if __name__ == '__main__':
    print("🚀 Test avancé de l'API Analytics")
    test_analytics_parameters()
    test_error_cases()
