#!/usr/bin/env python
"""
Script de test pour vérifier l'accès ouvert aux Analytics
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


def create_normal_user():
    """Créer un utilisateur normal sans permissions spéciales"""
    username = 'normal_user'
    email = 'normal@test.com'
    password = 'testpass123'
    
    # Créer ou récupérer l'utilisateur
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Normal',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Utilisateur normal créé: {username}")
    else:
        print(f"🔄 Utilisateur normal existant: {username}")
    
    # Créer ou récupérer le token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"✅ Token créé: {token.key}")
    else:
        print(f"🔄 Token existant: {token.key}")
    
    return user, token.key


def test_open_access():
    """Tester l'accès ouvert aux Analytics"""
    base_url = 'http://localhost:8000'
    
    # Créer l'utilisateur normal
    user, token = create_normal_user()
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    print(f"\n🧪 Test d'accès ouvert aux Analytics...")
    print(f"🔑 Token: {token}")
    print(f"👤 Utilisateur: {user.username}")
    print(f"🔐 Permissions: Aucune permission spéciale")
    
    endpoints = [
        {
            'name': 'Analytics Principal',
            'url': f'{base_url}/api/analytics/',
            'params': {'period': '30d'}
        },
        {
            'name': 'KPIs',
            'url': f'{base_url}/api/analytics/kpis/',
            'params': {'period': '30d'}
        },
        {
            'name': 'Graphique Revenus',
            'url': f'{base_url}/api/analytics/revenue-chart/',
            'params': {'period': '30d'}
        },
        {
            'name': 'Performance Ventes',
            'url': f'{base_url}/api/analytics/sales-performance/',
            'params': {'period': '30d'}
        },
        {
            'name': 'Top Clients',
            'url': f'{base_url}/api/analytics/top-customers/',
            'params': {'period': '30d'}
        },
        {
            'name': 'Top Produits',
            'url': f'{base_url}/api/analytics/top-products/',
            'params': {'period': '30d'}
        }
    ]
    
    success_count = 0
    total_count = len(endpoints)
    
    for endpoint in endpoints:
        try:
            print(f"\n📊 Test: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            
            response = requests.get(
                endpoint['url'],
                headers=headers,
                params=endpoint['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès (200) - Accès autorisé")
                print(f"   📄 Type de réponse: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"   🔑 Clés principales: {list(data.keys())}")
                    
                    # Afficher quelques données pour les KPIs
                    if 'total_sales' in data:
                        print(f"   💰 Chiffre d'affaires: {data['total_sales']:,} FCFA")
                    elif 'labels' in data and 'datasets' in data:
                        print(f"   📊 Labels: {len(data['labels'])} éléments")
                    elif isinstance(data, list) and len(data) > 0:
                        print(f"   📋 Nombre d'éléments: {len(data)}")
                
                success_count += 1
                
            elif response.status_code == 403:
                print(f"   ❌ Accès refusé (403) - Permission requise")
                error_data = response.json()
                print(f"   🔒 Erreur: {error_data.get('error', {}).get('message', 'N/A')}")
                
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
        print(f"   🎉 Tous les endpoints sont accessibles !")
    else:
        print(f"   ⚠️  Certains endpoints nécessitent encore des permissions")


if __name__ == '__main__':
    print("🚀 Test d'accès ouvert aux Analytics")
    test_open_access()
