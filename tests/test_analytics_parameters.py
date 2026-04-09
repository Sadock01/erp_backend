#!/usr/bin/env python
"""
Script de test pour vérifier que les paramètres Analytics fonctionnent
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
    """Tester que les paramètres Analytics changent les données"""
    base_url = 'http://localhost:8000'
    
    # Récupérer un utilisateur
    try:
        user = User.objects.first()
        if not user:
            user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='testpass123'
            )
        token = Token.objects.get_or_create(user=user)[0]
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur: {e}")
        return
    
    headers = {
        'Authorization': f'Token {token.key}',
        'Content-Type': 'application/json'
    }
    
    print(f"🧪 Test des paramètres Analytics...")
    print(f"🔑 Token: {token.key}")
    print(f"👤 Utilisateur: {user.username}")
    
    # Tests avec différents paramètres
    test_cases = [
        {
            'name': '7 jours',
            'params': {'period': '7d'},
            'expected_lower': True
        },
        {
            'name': '30 jours',
            'params': {'period': '30d'},
            'expected_lower': False
        },
        {
            'name': '90 jours',
            'params': {'period': '90d'},
            'expected_higher': True
        },
        {
            'name': '1 an',
            'params': {'period': '1y'},
            'expected_higher': True
        },
        {
            'name': 'Clients VIP',
            'params': {'period': '30d', 'customer_segment': 'vip'},
            'expected_higher': True
        },
        {
            'name': 'Nouveaux clients',
            'params': {'period': '30d', 'customer_segment': 'new'},
            'expected_lower': True
        },
        {
            'name': 'Catégorie Électronique',
            'params': {'period': '30d', 'product_category': 'electronics'},
            'expected_higher': True
        },
        {
            'name': 'Catégorie Vêtements',
            'params': {'period': '30d', 'product_category': 'clothing'},
            'expected_lower': True
        }
    ]
    
    results = {}
    
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
                kpis = data.get('kpis', {})
                total_sales = kpis.get('total_sales', 0)
                avg_order_value = kpis.get('avg_order_value', 0)
                
                print(f"   ✅ Succès (200)")
                print(f"   💰 CA Total: {total_sales:,} FCFA")
                print(f"   🛒 Panier moyen: {avg_order_value:,} FCFA")
                
                # Vérifier les graphiques
                if 'revenue_chart' in data:
                    chart = data['revenue_chart']
                    print(f"   📊 Graphique revenus: {len(chart.get('labels', []))} périodes")
                
                if 'sales_performance_chart' in data:
                    perf_chart = data['sales_performance_chart']
                    print(f"   📈 Performance: {len(perf_chart.get('labels', []))} catégories")
                
                # Vérifier les tableaux
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
                
                # Stocker les résultats pour comparaison
                results[test_case['name']] = {
                    'total_sales': total_sales,
                    'avg_order_value': avg_order_value,
                    'params': test_case['params']
                }
                
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
    
    # Analyser les résultats
    print(f"\n📊 Analyse des résultats:")
    if len(results) >= 2:
        # Comparer 7 jours vs 30 jours
        if '7 jours' in results and '30 jours' in results:
            sales_7d = results['7 jours']['total_sales']
            sales_30d = results['30 jours']['total_sales']
            if sales_7d < sales_30d:
                print(f"   ✅ 7 jours < 30 jours: {sales_7d:,} < {sales_30d:,} FCFA")
            else:
                print(f"   ⚠️  7 jours >= 30 jours: {sales_7d:,} >= {sales_30d:,} FCFA")
        
        # Comparer 30 jours vs 90 jours
        if '30 jours' in results and '90 jours' in results:
            sales_30d = results['30 jours']['total_sales']
            sales_90d = results['90 jours']['total_sales']
            if sales_90d > sales_30d:
                print(f"   ✅ 90 jours > 30 jours: {sales_90d:,} > {sales_30d:,} FCFA")
            else:
                print(f"   ⚠️  90 jours <= 30 jours: {sales_90d:,} <= {sales_30d:,} FCFA")
        
        # Comparer clients VIP vs normaux
        if 'Clients VIP' in results and '30 jours' in results:
            sales_vip = results['Clients VIP']['total_sales']
            sales_normal = results['30 jours']['total_sales']
            if sales_vip > sales_normal:
                print(f"   ✅ VIP > Normal: {sales_vip:,} > {sales_normal:,} FCFA")
            else:
                print(f"   ⚠️  VIP <= Normal: {sales_vip:,} <= {sales_normal:,} FCFA")
        
        # Comparer électronique vs vêtements
        if 'Catégorie Électronique' in results and 'Catégorie Vêtements' in results:
            sales_electronics = results['Catégorie Électronique']['total_sales']
            sales_clothing = results['Catégorie Vêtements']['total_sales']
            if sales_electronics > sales_clothing:
                print(f"   ✅ Électronique > Vêtements: {sales_electronics:,} > {sales_clothing:,} FCFA")
            else:
                print(f"   ⚠️  Électronique <= Vêtements: {sales_electronics:,} <= {sales_clothing:,} FCFA")
    
    print(f"\n🎯 Test des paramètres terminé!")


if __name__ == '__main__':
    print("🚀 Test des paramètres Analytics")
    test_analytics_parameters()

