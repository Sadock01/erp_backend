#!/usr/bin/env python
"""
Script de test pour vérifier le graphique des revenus
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


def test_revenue_chart():
    """Tester le graphique des revenus avec différents paramètres"""
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
    
    print(f"🧪 Test du graphique des revenus...")
    print(f"🔑 Token: {token.key}")
    print(f"👤 Utilisateur: {user.username}")
    
    # Tests avec différents paramètres
    test_cases = [
        {
            'name': '7 jours',
            'params': {'period': '7d'},
            'expected_labels': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        },
        {
            'name': '30 jours',
            'params': {'period': '30d'},
            'expected_labels': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4']
        },
        {
            'name': '90 jours',
            'params': {'period': '90d'},
            'expected_labels': ['Mois 1', 'Mois 2', 'Mois 3']
        },
        {
            'name': '1 an',
            'params': {'period': '1y'},
            'expected_labels': ['Q1', 'Q2', 'Q3', 'Q4']
        }
    ]
    
    for test_case in test_cases:
        try:
            print(f"\n📊 Test: {test_case['name']}")
            print(f"   Paramètres: {test_case['params']}")
            
            response = requests.get(
                f'{base_url}/api/analytics/revenue-chart/',
                headers=headers,
                params=test_case['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                labels = data.get('labels', [])
                datasets = data.get('datasets', [])
                
                print(f"   ✅ Succès (200)")
                print(f"   📊 Labels: {labels}")
                print(f"   📈 Nombre de périodes: {len(labels)}")
                
                if datasets and len(datasets) > 0:
                    chart_data = datasets[0].get('data', [])
                    print(f"   💰 Données: {chart_data}")
                    print(f"   📊 Nombre de points: {len(chart_data)}")
                
                # Vérifier si les labels correspondent
                expected_labels = test_case['expected_labels']
                if labels == expected_labels:
                    print(f"   ✅ Labels corrects: {labels}")
                else:
                    print(f"   ⚠️  Labels inattendus:")
                    print(f"      Attendu: {expected_labels}")
                    print(f"      Reçu: {labels}")
                
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
    
    print(f"\n🎯 Test du graphique des revenus terminé!")


if __name__ == '__main__':
    print("🚀 Test du graphique des revenus")
    test_revenue_chart()

