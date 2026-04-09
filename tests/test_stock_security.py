#!/usr/bin/env python
"""
Script pour tester la sécurisation de l'API Stock
Usage: python test_stock_security.py
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

def test_stock_security():
    """Test la sécurisation de l'API Stock"""
    
    print("=" * 60)
    print("🔒 TEST DE SÉCURISATION - API Stock")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Test sans authentification
    print(f"\n1️⃣ TEST SANS AUTHENTIFICATION:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/stock/movements/")
        print(f"GET /api/stock/movements/ - Status: {response.status_code}")
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
    test_email = f'test_stock_{random_suffix}@example.com'
    test_username = f'test_stock_{random_suffix}'
    
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
            
            # Tester l'accès aux mouvements
            response = requests.get(f"{base_url}/api/stock/movements/", headers=headers)
            print(f"GET /api/stock/movements/ - Status: {response.status_code}")
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
    
    # Assigner le rôle Stock Manager (qui a stock_movements_view)
    try:
        stock_manager_role = Role.objects.get(name='Stock Manager')
        permission = Permission.objects.get(codename='stock_movements_view')
        
        # Créer l'assignation de rôle
        user_role, created = UserRole.objects.get_or_create(
            user=test_user,
            role=stock_manager_role,
            defaults={'assigned_by': test_user}
        )
        
        # Assigner la permission au rôle
        role_permission, created = RolePermission.objects.get_or_create(
            role=stock_manager_role,
            permission=permission,
            defaults={'granted': True}
        )
        
        print(f"✅ Rôle '{stock_manager_role.name}' assigné à l'utilisateur")
        print(f"✅ Permission '{permission.name}' accordée au rôle")
        
        # Tester l'accès
        if headers:
            response = requests.get(f"{base_url}/api/stock/movements/", headers=headers)
            print(f"GET /api/stock/movements/ - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Accès autorisé !")
                data = response.json()
                print(f"   Nombre de mouvements: {data.get('count', 'N/A')}")
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
        # Movements
        ('GET', '/api/stock/movements/', 'stock_movements_view', 'Lister les mouvements'),
        ('POST', '/api/stock/movements/', 'stock_movements_create', 'Créer un mouvement'),
        ('GET', '/api/stock/movements/1/', 'stock_movements_view', 'Voir un mouvement'),
        ('PUT', '/api/stock/movements/1/', 'stock_movements_create', 'Modifier un mouvement'),
        ('DELETE', '/api/stock/movements/1/', 'stock_movements_create', 'Supprimer un mouvement'),
        ('GET', '/api/stock/movements/entries/', 'stock_movements_view', 'Lister les entrées'),
        ('GET', '/api/stock/movements/exits/', 'stock_movements_view', 'Lister les sorties'),
        ('GET', '/api/stock/movements/pending_approval/', 'stock_movements_view', 'Mouvements en attente'),
        ('GET', '/api/stock/movements/summary/', 'stock_movements_view', 'Résumé des mouvements'),
        
        # Adjustments
        ('GET', '/api/stock/adjustments/', 'stock_adjustments_manage', 'Lister les ajustements'),
        ('POST', '/api/stock/adjustments/', 'stock_adjustments_manage', 'Créer un ajustement'),
        ('GET', '/api/stock/adjustments/1/', 'stock_adjustments_manage', 'Voir un ajustement'),
        ('PUT', '/api/stock/adjustments/1/', 'stock_adjustments_manage', 'Modifier un ajustement'),
        ('DELETE', '/api/stock/adjustments/1/', 'stock_adjustments_manage', 'Supprimer un ajustement'),
        ('GET', '/api/stock/adjustments/pending_approval/', 'stock_adjustments_manage', 'Ajustements en attente'),
        ('GET', '/api/stock/adjustments/summary/', 'stock_adjustments_manage', 'Résumé des ajustements'),
        
        # Alerts
        ('GET', '/api/stock/alerts/', 'stock_alerts_manage', 'Lister les alertes'),
        ('POST', '/api/stock/alerts/', 'stock_alerts_manage', 'Créer une alerte'),
        ('GET', '/api/stock/alerts/1/', 'stock_alerts_manage', 'Voir une alerte'),
        ('PUT', '/api/stock/alerts/1/', 'stock_alerts_manage', 'Modifier une alerte'),
        ('DELETE', '/api/stock/alerts/1/', 'stock_alerts_manage', 'Supprimer une alerte'),
        ('GET', '/api/stock/alerts/active/', 'stock_alerts_manage', 'Alertes actives'),
        ('GET', '/api/stock/alerts/resolved/', 'stock_alerts_manage', 'Alertes résolues'),
        ('GET', '/api/stock/alerts/summary/', 'stock_alerts_manage', 'Résumé des alertes'),
        
        # Reports
        ('GET', '/api/stock/reports/', 'stock_reports_manage', 'Lister les rapports'),
        ('POST', '/api/stock/reports/', 'stock_reports_manage', 'Créer un rapport'),
        ('GET', '/api/stock/reports/1/', 'stock_reports_manage', 'Voir un rapport'),
        ('PUT', '/api/stock/reports/1/', 'stock_reports_manage', 'Modifier un rapport'),
        ('DELETE', '/api/stock/reports/1/', 'stock_reports_manage', 'Supprimer un rapport'),
        ('GET', '/api/stock/reports/summary/', 'stock_reports_manage', 'Résumé des rapports'),
    ]
    
    for method, endpoint, required_permission, description in actions:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == 'POST':
                # Données de test appropriées selon l'endpoint
                if 'movements' in endpoint:
                    data = {'product': 1, 'quantity': 10, 'movement_type': 'in'}
                elif 'adjustments' in endpoint:
                    data = {'product': 1, 'adjustment_quantity': 5, 'adjustment_type': 'increase', 'reason': 'Test'}
                elif 'alerts' in endpoint:
                    data = {'product': 1, 'alert_type': 'low_stock', 'threshold_quantity': 10}
                elif 'reports' in endpoint:
                    data = {'title': 'Test Report', 'report_type': 'inventory', 'description': 'Test report'}
                else:
                    data = {}
                response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
            elif method == 'PUT':
                data = {'quantity': 20} if 'movements' in endpoint else {'title': 'Updated'}
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
        ('stock_movements_view', 'Voir les mouvements'),
        ('stock_movements_create', 'Créer des mouvements'),
        ('stock_adjustments_manage', 'Gérer les ajustements'),
        ('stock_alerts_manage', 'Gérer les alertes'),
        ('stock_reports_manage', 'Gérer les rapports'),
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
            'stock_movements_view', 'stock_movements_create',
            'stock_adjustments_manage', 'stock_alerts_manage', 'stock_reports_manage'
        ]
        
        for perm_codename in permissions_to_assign:
            permission = Permission.objects.get(codename=perm_codename)
            role_permission, created = RolePermission.objects.get_or_create(
                role=stock_manager_role,
                permission=permission,
                defaults={'granted': True}
            )
            if created:
                print(f"✅ Permission '{perm_codename}' assignée au rôle")
        
        # Tester la création d'un mouvement
        if headers:
            movement_data = {
                'product': 1,
                'quantity': 50,
                'movement_type': 'in',
                'reference': 'TEST-001',
                'notes': 'Test de création'
            }
            
            response = requests.post(f"{base_url}/api/stock/movements/", 
                                   json=movement_data, headers=headers)
            print(f"POST /api/stock/movements/ - Status: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ Mouvement créé avec succès !")
            elif response.status_code == 400:
                print("⚠️  Erreur de validation (normal si pas de produit)")
                print(f"   Détails: {response.json()}")
            else:
                print(f"❌ Erreur inattendue: {response.status_code}")
                print(f"   Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'assignation des permissions: {e}")
    
    print(f"\n" + "=" * 60)
    print("✅ Test de sécurisation de l'API Stock terminé !")
    print("=" * 60)
    
    # Résumé des permissions requises
    print(f"\n📋 RÉSUMÉ DES PERMISSIONS REQUISES:")
    print("-" * 40)
    print("• stock_movements_view - Voir les mouvements de stock")
    print("• stock_movements_create - Créer/modifier/supprimer les mouvements")
    print("• stock_adjustments_manage - Gérer les ajustements de stock")
    print("• stock_alerts_manage - Gérer les alertes de stock")
    print("• stock_reports_manage - Gérer les rapports de stock")

if __name__ == "__main__":
    try:
        test_stock_security()
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        sys.exit(1)