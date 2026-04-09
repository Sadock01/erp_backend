#!/usr/bin/env python
"""
Script pour tester la sécurisation de l'API Inventory
Usage: python test_inventory_security.py
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

def test_inventory_security():
    """Test la sécurisation de l'API Inventory"""
    
    print("=" * 60)
    print("🔒 TEST DE SÉCURISATION - API Inventory")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Test sans authentification
    print(f"\n1️⃣ TEST SANS AUTHENTIFICATION:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/inventory/categories/")
        print(f"GET /api/inventory/categories/ - Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Correctement bloqué (403 Forbidden)")
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
    test_email = f'test_inventory_{random_suffix}@example.com'
    test_username = f'test_inventory_{random_suffix}'
    
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
            
            # Tester l'accès aux catégories
            response = requests.get(f"{base_url}/api/inventory/categories/", headers=headers)
            print(f"GET /api/inventory/categories/ - Status: {response.status_code}")
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
    
    # Assigner le rôle Viewer (qui a inventory_view)
    try:
        viewer_role = Role.objects.get(name='Viewer')
        permission = Permission.objects.get(codename='inventory_view')
        
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
            response = requests.get(f"{base_url}/api/inventory/categories/", headers=headers)
            print(f"GET /api/inventory/categories/ - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Accès autorisé !")
                data = response.json()
                print(f"   Nombre de catégories: {data.get('count', 'N/A')}")
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
        # Categories
        ('GET', '/api/inventory/categories/', 'inventory_category.view', 'Lister les catégories'),
        ('POST', '/api/inventory/categories/', 'inventory_category.create', 'Créer une catégorie'),
        ('GET', '/api/inventory/categories/1/', 'inventory_category.view', 'Voir une catégorie'),
        ('PUT', '/api/inventory/categories/1/', 'inventory_category.update', 'Modifier une catégorie'),
        ('DELETE', '/api/inventory/categories/1/', 'inventory_category.delete', 'Supprimer une catégorie'),
        
        # Products
        ('GET', '/api/inventory/products/', 'inventory_view', 'Lister les produits'),
        ('POST', '/api/inventory/products/', 'inventory_create', 'Créer un produit'),
        ('GET', '/api/inventory/products/1/', 'inventory_view', 'Voir un produit'),
        ('PUT', '/api/inventory/products/1/', 'inventory_update', 'Modifier un produit'),
        ('DELETE', '/api/inventory/products/1/', 'inventory_delete', 'Supprimer un produit'),
        
        # Variants
        ('GET', '/api/inventory/variants/', 'inventory_variant.view', 'Lister les variants'),
        ('POST', '/api/inventory/variants/', 'inventory_variant.create', 'Créer un variant'),
        ('GET', '/api/inventory/variants/1/', 'inventory_variant.view', 'Voir un variant'),
        ('PUT', '/api/inventory/variants/1/', 'inventory_variant.update', 'Modifier un variant'),
        ('DELETE', '/api/inventory/variants/1/', 'inventory_variant.delete', 'Supprimer un variant'),
    ]
    
    for method, endpoint, required_permission, description in actions:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == 'POST':
                response = requests.post(f"{base_url}{endpoint}", 
                    json={'name': f'Test {random_suffix}', 'description': 'Test description'}, 
                    headers=headers)
            elif method == 'PUT':
                response = requests.put(f"{base_url}{endpoint}", 
                    json={'name': f'Test Updated {random_suffix}'}, 
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
        test_inventory_security()
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        sys.exit(1)
