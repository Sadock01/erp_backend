#!/usr/bin/env python
"""
Script de test pour l'API Analytics
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
from apps.permissions.models import Role, Permission, RolePermission, UserRole


def create_test_user():
    """Créer un utilisateur de test avec les permissions Analytics"""
    username = 'analytics_test'
    email = 'analytics@test.com'
    password = 'testpass123'
    
    # Créer ou récupérer l'utilisateur
    user, created = User.objects.get_or_create(
        username=username,
        defaults={
            'email': email,
            'first_name': 'Analytics',
            'last_name': 'Test',
            'is_active': True
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print(f"✅ Utilisateur créé: {username}")
    else:
        print(f"🔄 Utilisateur existant: {username}")
    
    # Créer ou récupérer le token
    token, created = Token.objects.get_or_create(user=user)
    if created:
        print(f"✅ Token créé: {token.key}")
    else:
        print(f"🔄 Token existant: {token.key}")
    
    # Créer le rôle Analytics
    role, created = Role.objects.get_or_create(
        name='Analytics Manager',
        defaults={
            'description': 'Gestionnaire des analytics',
            'is_active': True,
            'level': 1,
            'color': '#10B981',
            'icon': 'fas fa-chart-line'
        }
    )
    
    if created:
        print(f"✅ Rôle créé: {role.name}")
    else:
        print(f"🔄 Rôle existant: {role.name}")
    
    # Assigner le rôle à l'utilisateur
    user_role, created = UserRole.objects.get_or_create(
        user=user,
        role=role
    )
    
    if created:
        print(f"✅ Rôle assigné à l'utilisateur")
    else:
        print(f"🔄 Rôle déjà assigné")
    
    # Assigner les permissions Analytics
    analytics_permissions = Permission.objects.filter(
        codename__in=['analytics:read', 'analytics:manage']
    )
    
    for perm in analytics_permissions:
        role_perm, created = RolePermission.objects.get_or_create(
            role=role,
            permission=perm,
            defaults={'granted': True}
        )
        
        if created:
            print(f"✅ Permission assignée: {perm.name}")
        else:
            print(f"🔄 Permission déjà assignée: {perm.name}")
    
    return user, token.key


def test_analytics_endpoints():
    """Tester tous les endpoints Analytics"""
    base_url = 'http://localhost:8000'
    
    # Créer l'utilisateur de test
    user, token = create_test_user()
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
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
            'params': {'period': '30d', 'customer_segment': 'vip'}
        },
        {
            'name': 'Top Produits',
            'url': f'{base_url}/api/analytics/top-products/',
            'params': {'period': '30d', 'product_category': 'electronics'}
        }
    ]
    
    print(f"\n🧪 Test des endpoints Analytics...")
    print(f"🔑 Token: {token}")
    print(f"👤 Utilisateur: {user.username}")
    
    for endpoint in endpoints:
        try:
            print(f"\n📊 Test: {endpoint['name']}")
            print(f"   URL: {endpoint['url']}")
            print(f"   Paramètres: {endpoint['params']}")
            
            response = requests.get(
                endpoint['url'],
                headers=headers,
                params=endpoint['params'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Succès (200)")
                print(f"   📄 Type de réponse: {type(data)}")
                
                if isinstance(data, dict):
                    print(f"   🔑 Clés principales: {list(data.keys())}")
                    
                    # Afficher quelques données pour les KPIs
                    if 'total_sales' in data:
                        print(f"   💰 Chiffre d'affaires: {data['total_sales']} FCFA")
                    elif 'labels' in data and 'datasets' in data:
                        print(f"   📊 Labels: {len(data['labels'])} éléments")
                        print(f"   📈 Datasets: {len(data['datasets'])} séries")
                    elif isinstance(data, list) and len(data) > 0:
                        print(f"   📋 Nombre d'éléments: {len(data)}")
                        if 'rank' in data[0]:
                            print(f"   🏆 Premier élément: {data[0].get('name', 'N/A')}")
                
            elif response.status_code == 403:
                print(f"   ❌ Accès refusé (403)")
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
    
    print(f"\n🎯 Test terminé!")


if __name__ == '__main__':
    print("🚀 Test de l'API Analytics")
    test_analytics_endpoints()
