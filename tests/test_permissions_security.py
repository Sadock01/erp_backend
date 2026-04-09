#!/usr/bin/env python
"""
Script pour tester la sécurisation de l'API Permissions
Usage: python test_permissions_security.py
"""

import os
import sys
import django
import requests
import json
import random
import string

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from apps.permissions.models import Role, Permission, UserRole, RolePermission

def test_permissions_security():
    """Test la sécurisation de l'API Permissions"""
    
    print("=" * 60)
    print("🔒 TEST DE SÉCURISATION - API Permissions")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Test sans authentification
    print(f"\n1️⃣ TEST SANS AUTHENTIFICATION:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/permissions/roles/")
        print(f"GET /api/permissions/roles/ - Status: {response.status_code}")
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
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    test_email = f'test_permissions_{random_suffix}@example.com'
    test_username = f'test_permissions_{random_suffix}'
    
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
            
            # Tester l'accès aux rôles
            response = requests.get(f"{base_url}/api/permissions/roles/", headers=headers)
            print(f"GET /api/permissions/roles/ - Status: {response.status_code}")
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
    
    # Assigner le rôle Admin (qui a permissions_roles_view)
    try:
        admin_role = Role.objects.get(name='Admin')
        permission = Permission.objects.get(codename='permissions_roles_view')
        
        # Créer l'assignation de rôle
        user_role, created = UserRole.objects.get_or_create(
            user=test_user,
            role=admin_role,
            defaults={'assigned_by': test_user}
        )
        
        # Assigner la permission au rôle
        role_permission, created = RolePermission.objects.get_or_create(
            role=admin_role,
            permission=permission,
            defaults={'granted': True}
        )
        
        print(f"✅ Rôle '{admin_role.name}' assigné à l'utilisateur")
        print(f"✅ Permission '{permission.name}' accordée au rôle")
        
        # Tester l'accès
        if headers:
            response = requests.get(f"{base_url}/api/permissions/roles/", headers=headers)
            print(f"GET /api/permissions/roles/ - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Accès autorisé !")
                data = response.json()
                print(f"   Nombre de rôles: {data.get('count', 'N/A')}")
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
        # Roles
        ('GET', '/api/permissions/roles/', 'permissions_roles_view', 'Lister les rôles'),
        ('POST', '/api/permissions/roles/', 'permissions_roles_manage', 'Créer un rôle'),
        ('GET', '/api/permissions/roles/1/', 'permissions_roles_view', 'Voir un rôle'),
        ('PUT', '/api/permissions/roles/1/', 'permissions_roles_manage', 'Modifier un rôle'),
        ('DELETE', '/api/permissions/roles/1/', 'permissions_roles_manage', 'Supprimer un rôle'),
        ('GET', '/api/permissions/roles/active/', 'permissions_roles_view', 'Rôles actifs'),
        ('GET', '/api/permissions/roles/system/', 'permissions_roles_view', 'Rôles système'),
        ('GET', '/api/permissions/roles/1/permissions/', 'permissions_roles_view', 'Permissions d\'un rôle'),
        
        # Permissions
        ('GET', '/api/permissions/permissions/', 'permissions_permissions_view', 'Lister les permissions'),
        ('POST', '/api/permissions/permissions/', 'permissions_permissions_manage', 'Créer une permission'),
        ('GET', '/api/permissions/permissions/1/', 'permissions_permissions_view', 'Voir une permission'),
        ('PUT', '/api/permissions/permissions/1/', 'permissions_permissions_manage', 'Modifier une permission'),
        ('DELETE', '/api/permissions/permissions/1/', 'permissions_permissions_manage', 'Supprimer une permission'),
        ('GET', '/api/permissions/permissions/by_app/', 'permissions_permissions_view', 'Permissions par app'),
        ('GET', '/api/permissions/permissions/active/', 'permissions_permissions_view', 'Permissions actives'),
        
        # User Roles
        ('GET', '/api/permissions/user-roles/', 'permissions_user_roles_view', 'Lister les rôles utilisateurs'),
        ('POST', '/api/permissions/user-roles/', 'permissions_user_roles_manage', 'Assigner un rôle'),
        ('GET', '/api/permissions/user-roles/1/', 'permissions_user_roles_view', 'Voir un rôle utilisateur'),
        ('PUT', '/api/permissions/user-roles/1/', 'permissions_user_roles_manage', 'Modifier un rôle utilisateur'),
        ('DELETE', '/api/permissions/user-roles/1/', 'permissions_user_roles_manage', 'Supprimer un rôle utilisateur'),
        ('GET', '/api/permissions/user-roles/active/', 'permissions_user_roles_view', 'Rôles utilisateurs actifs'),
        ('GET', '/api/permissions/user-roles/expired/', 'permissions_user_roles_view', 'Rôles utilisateurs expirés'),
        
        # Logs
        ('GET', '/api/permissions/logs/', 'permissions_logs_view', 'Lister les logs'),
        ('GET', '/api/permissions/logs/1/', 'permissions_logs_view', 'Voir un log'),
        
        # Stats
        ('GET', '/api/permissions/stats/', 'permissions_stats_view', 'Statistiques des permissions'),
        ('GET', '/api/permissions/user-permissions/1/', 'permissions_user_roles_view', 'Permissions d\'un utilisateur'),
    ]
    
    for method, endpoint, required_permission, description in actions:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == 'POST':
                # Données de test appropriées selon l'endpoint
                if 'roles' in endpoint:
                    data = {'name': 'Test Role', 'description': 'Test role', 'level': 1}
                elif 'permissions' in endpoint:
                    data = {'name': 'Test Permission', 'codename': 'test_permission', 'app_label': 'test'}
                elif 'user-roles' in endpoint:
                    data = {'user': 1, 'role': 1}
                else:
                    data = {}
                response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
            elif method == 'PUT':
                data = {'name': 'Updated Role'} if 'roles' in endpoint else {'name': 'Updated Permission'}
                response = requests.put(f"{base_url}{endpoint}", json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(f"{base_url}{endpoint}", headers=headers)
            
            print(f"{method} {endpoint}")
            print(f"   {description} - Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                print("   ✅ Accès autorisé")
            elif response.status_code == 403:
                print("   ✅ Correctement bloqué (403 Forbidden)")
                try:
                    error_data = response.json()
                    print(f"   📝 Message: {error_data.get('detail', 'N/A')}")
                    print(f"   🔑 Permission requise: {error_data.get('required_permission', 'N/A')}")
                except:
                    pass
            elif response.status_code == 404:
                print("   ⚠️  Ressource non trouvée (normal si pas de données)")
            else:
                print(f"   ❓ Status inattendu: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
    
    # 5. Test des permissions spécifiques
    print(f"\n5️⃣ TEST DES PERMISSIONS SPÉCIFIQUES:")
    print("-" * 45)
    
    # Tester avec différentes permissions
    test_permissions = [
        ('permissions_roles_view', 'Voir les rôles'),
        ('permissions_roles_manage', 'Gérer les rôles'),
        ('permissions_permissions_view', 'Voir les permissions'),
        ('permissions_permissions_manage', 'Gérer les permissions'),
        ('permissions_user_roles_view', 'Voir les rôles utilisateurs'),
        ('permissions_user_roles_manage', 'Gérer les rôles utilisateurs'),
        ('permissions_logs_view', 'Voir les logs de permissions'),
        ('permissions_stats_view', 'Voir les statistiques de permissions'),
    ]
    
    for permission_codename, description in test_permissions:
        try:
            # Vérifier si la permission existe
            permission = Permission.objects.filter(codename=permission_codename).first()
            if permission:
                print(f"✅ Permission '{permission_codename}' existe: {permission.name}")
            else:
                print(f"❌ Permission '{permission_codename}' manquante")
        except Exception as e:
            print(f"❌ Erreur lors de la vérification de '{permission_codename}': {e}")
    
    # 6. Test de création de données avec permissions
    print(f"\n6️⃣ TEST DE CRÉATION AVEC PERMISSIONS:")
    print("-" * 45)
    
    # Assigner toutes les permissions nécessaires
    try:
        permissions_to_assign = [
            'permissions_roles_view', 'permissions_roles_manage',
            'permissions_permissions_view', 'permissions_permissions_manage',
            'permissions_user_roles_view', 'permissions_user_roles_manage',
            'permissions_logs_view', 'permissions_stats_view'
        ]
        
        for perm_codename in permissions_to_assign:
            permission = Permission.objects.get(codename=perm_codename)
            role_permission, created = RolePermission.objects.get_or_create(
                role=admin_role,
                permission=permission,
                defaults={'granted': True}
            )
            if created:
                print(f"✅ Permission '{perm_codename}' assignée au rôle")
        
        # Tester la création d'un rôle
        if headers:
            role_data = {
                'name': 'Test Security Role',
                'description': 'Rôle de test pour la sécurisation',
                'level': 5
            }
            
            response = requests.post(f"{base_url}/api/permissions/roles/", 
                                   json=role_data, headers=headers)
            print(f"POST /api/permissions/roles/ - Status: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ Rôle créé avec succès !")
            elif response.status_code == 400:
                print("⚠️  Erreur de validation (normal si nom existe déjà)")
                print(f"   Détails: {response.json()}")
            else:
                print(f"❌ Erreur inattendue: {response.status_code}")
                print(f"   Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'assignation des permissions: {e}")
    
    print(f"\n" + "=" * 60)
    print("✅ Test de sécurisation de l'API Permissions terminé !")
    print("=" * 60)
    
    # Résumé des permissions requises
    print(f"\n📋 RÉSUMÉ DES PERMISSIONS REQUISES:")
    print("-" * 40)
    print("• permissions_roles_view - Voir les rôles")
    print("• permissions_roles_manage - Gérer les rôles")
    print("• permissions_permissions_view - Voir les permissions")
    print("• permissions_permissions_manage - Gérer les permissions")
    print("• permissions_user_roles_view - Voir les rôles utilisateurs")
    print("• permissions_user_roles_manage - Gérer les rôles utilisateurs")
    print("• permissions_logs_view - Voir les logs de permissions")
    print("• permissions_stats_view - Voir les statistiques de permissions")

if __name__ == "__main__":
    try:
        test_permissions_security()
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        sys.exit(1)
