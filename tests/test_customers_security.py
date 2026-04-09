#!/usr/bin/env python
"""
Script pour tester la sécurisation de l'API Customers
Usage: python test_customers_security.py
"""

import os
import sys
import django
import requests
import json

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from apps.permissions.models import Role, Permission, UserRole, RolePermission

def test_customers_security():
    """Test la sécurisation de l'API Customers"""
    
    print("=" * 60)
    print("🔒 TEST DE SÉCURISATION - API Customers")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Test sans authentification
    print(f"\n1️⃣ TEST SANS AUTHENTIFICATION:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/customers/")
        print(f"GET /api/customers/ - Status: {response.status_code}")
        if response.status_code == 401:
            print("✅ Correctement bloqué (401 Unauthorized)")
        else:
            print("❌ PROBLÈME: Devrait être bloqué !")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return
    
    # 2. Test avec authentification mais sans permissions
    print(f"\n2️⃣ TEST AVEC AUTHENTIFICATION SANS PERMISSIONS:")
    print("-" * 50)
    
    # Créer un utilisateur de test sans permissions avec email aléatoire
    import random
    import string
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f'test_no_permissions_{random_suffix}@example.com'
    test_username = f'test_no_permissions_{random_suffix}'
    
    test_user, created = User.objects.get_or_create(
        username=test_username,
        defaults={'email': test_email, 'is_active': True}
    )
    if created:
        test_user.set_password('test123')
        test_user.save()
        print(f"✅ Utilisateur de test créé: {test_email}")
    else:
        print(f"✅ Utilisateur de test existant: {test_email}")
    
    # Obtenir un token pour cet utilisateur
    headers = None
    try:
        login_response = requests.post(f"{base_url}/api/auth/login/", {
            'email': test_user.email,
            'password': 'test123'
        })
        
        if login_response.status_code == 200:
            token = login_response.json()['token']
            headers = {'Authorization': f'Token {token}'}
            print(f"✅ Token obtenu pour {test_email}")
            
            # Tester l'accès aux clients
            response = requests.get(f"{base_url}/api/customers/", headers=headers)
            print(f"GET /api/customers/ - Status: {response.status_code}")
            if response.status_code == 403:
                print("✅ Correctement bloqué (403 Forbidden)")
                print(f"   Message: {response.json().get('detail', 'N/A')}")
            else:
                print("❌ PROBLÈME: Devrait être bloqué !")
        else:
            print(f"❌ Erreur de connexion: {login_response.status_code}")
            print(f"   Réponse: {login_response.text}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    # 3. Test avec permissions appropriées
    print(f"\n3️⃣ TEST AVEC PERMISSIONS APPROPRIÉES:")
    print("-" * 45)
    
    # Assigner le rôle Viewer (qui a customers_view)
    try:
        viewer_role = Role.objects.get(name='Viewer')
        permission = Permission.objects.get(codename='customers_view')
        
        # Créer l'assignation de rôle
        user_role, created = UserRole.objects.get_or_create(
            user=test_user,
            role=viewer_role,
            defaults={'assigned_by': test_user}
        )
        
        # Assigner la permission au rôle
        role_permission, created = RolePermission.objects.get_or_create(
            role=viewer_role,
            permission=permission,
            defaults={'granted': True}
        )
        
        print(f"✅ Rôle '{viewer_role.name}' assigné à l'utilisateur")
        print(f"✅ Permission '{permission.name}' accordée au rôle")
        
        # Tester l'accès
        if headers:
            response = requests.get(f"{base_url}/api/customers/", headers=headers)
            print(f"GET /api/customers/ - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Accès autorisé !")
                data = response.json()
                print(f"   Nombre de clients: {data.get('count', 'N/A')}")
            else:
                print(f"❌ PROBLÈME: Devrait être autorisé !")
                print(f"   Réponse: {response.text}")
        else:
            print("❌ Pas de headers d'authentification disponibles")
            
    except Exception as e:
        print(f"❌ Erreur lors de l'assignation des permissions: {e}")
    
    # 4. Test des différentes actions
    print(f"\n4️⃣ TEST DES DIFFÉRENTES ACTIONS:")
    print("-" * 40)
    
    if not headers:
        print("❌ Pas de headers d'authentification disponibles pour les tests")
        return
    
    actions = [
        ('GET', '/api/customers/', 'customers_view', 'Lister les clients'),
        ('POST', '/api/customers/', 'customers_create', 'Créer un client'),
        ('GET', '/api/customers/1/', 'customers_view', 'Voir un client'),
        ('PUT', '/api/customers/1/', 'customers_update', 'Modifier un client'),
        ('DELETE', '/api/customers/1/', 'customers_delete', 'Supprimer un client'),
    ]
    
    for method, endpoint, required_permission, description in actions:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == 'POST':
                response = requests.post(f"{base_url}{endpoint}", 
                    json={'first_name': 'Test', 'last_name': 'User', 'email': f'test_{random_suffix}@test.com'}, 
                    headers=headers)
            elif method == 'PUT':
                response = requests.put(f"{base_url}{endpoint}", 
                    json={'first_name': 'Test Updated'}, 
                    headers=headers)
            elif method == 'DELETE':
                response = requests.delete(f"{base_url}{endpoint}", headers=headers)
            
            print(f"{method} {endpoint}")
            print(f"   {description} - Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("   ✅ Accès autorisé")
            elif response.status_code == 403:
                print("   ✅ Correctement bloqué (403 Forbidden)")
            elif response.status_code == 404:
                print("   ⚠️  Ressource non trouvée (normal si pas de données)")
            else:
                print(f"   ❓ Status inattendu: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    print(f"\n" + "=" * 60)
    print("✅ Test de sécurisation terminé !")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_customers_security()
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        sys.exit(1)
