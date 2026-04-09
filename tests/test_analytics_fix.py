#!/usr/bin/env python
"""
Script de test pour vérifier la correction de l'erreur
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


def test_analytics_fix():
    """Tester que l'erreur de comparaison est corrigée"""
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
    
    print(f"🧪 Test de la correction de l'erreur...")
    print(f"🔑 Token: {token.key}")
    print(f"👤 Utilisateur: {user.username}")
    
    # Tests avec différents paramètres qui pourraient causer l'erreur
    test_cases = [
        {
            'name': 'Paramètres normaux',
            'params': {'period': '30d'}
        },
        {
            'name': 'Avec filtres de revenus',
            'params': {
                'period': '30d',
                'revenue_min': '1000000',
                'revenue_max': '5000000'
            }
        },
        {
            'name': 'Avec tous les filtres',
            'params': {
                'period': '30d',
                'customer_segment': 'vip',
                'product_category': 'electronics',
                'revenue_min': '2000000',
                'revenue_max': '8000000'
            }
        },
        {
            'name': 'Période 7 jours',
            'params': {'period': '7d'}
        },
        {
            'name': 'Période 90 jours',
            'params': {'period': '90d'}
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
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
                    total_sales = kpis.get('total_sales', 0)
                    print(f"   💰 CA Total: {total_sales:,} FCFA")
                
                if 'revenue_chart' in data:
                    chart = data['revenue_chart']
                    labels = chart.get('labels', [])
                    print(f"   📊 Graphique: {len(labels)} périodes")
                
                success_count += 1
                
            elif response.status_code == 500:
                print(f"   ❌ Erreur serveur (500)")
                try:
                    error_data = response.json()
                    print(f"   📄 Erreur: {error_data.get('error', {}).get('message', 'N/A')}")
                    print(f"   🔍 Détails: {error_data.get('error', {}).get('details', 'N/A')}")
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
    
    print(f"\n🎯 Résumé du test:")
    print(f"   ✅ Succès: {success_count}/{total_count}")
    print(f"   📊 Taux de réussite: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print(f"   🎉 Tous les tests ont réussi ! L'erreur est corrigée.")
    else:
        print(f"   ⚠️  Certains tests ont échoué. Vérifiez les erreurs ci-dessus.")


if __name__ == '__main__':
    print("🚀 Test de correction de l'erreur Analytics")
    test_analytics_fix()

