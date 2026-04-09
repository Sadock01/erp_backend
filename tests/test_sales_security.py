#!/usr/bin/env python
"""
Script pour tester la sécurisation de l'API Sales
Usage: python test_sales_security.py
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

def test_sales_security():
    """Test la sécurisation de l'API Sales"""
    
    print("=" * 60)
    print("🔒 TEST DE SÉCURISATION - API Sales")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # 1. Test sans authentification
    print(f"\n1️⃣ TEST SANS AUTHENTIFICATION:")
    print("-" * 40)
    
    try:
        response = requests.get(f"{base_url}/api/sales/orders/")
        print(f"GET /api/sales/orders/ - Status: {response.status_code}")
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
    test_email = f'test_sales_{random_suffix}@example.com'
    test_username = f'test_sales_{random_suffix}'
    
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
            
            # Tester l'accès aux commandes
            response = requests.get(f"{base_url}/api/sales/orders/", headers=headers)
            print(f"GET /api/sales/orders/ - Status: {response.status_code}")
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
    
    # Assigner le rôle Sales Manager (qui a sales_orders_view)
    try:
        sales_manager_role = Role.objects.get(name='Sales Manager')
        permission = Permission.objects.get(codename='sales_orders_view')
        
        # Créer l'assignation de rôle
        user_role, created = UserRole.objects.get_or_create(
            user=test_user,
            role=sales_manager_role,
            defaults={'assigned_by': test_user}
        )
        
        # Assigner la permission au rôle
        role_permission, created = RolePermission.objects.get_or_create(
            role=sales_manager_role,
            permission=permission,
            defaults={'granted': True}
        )
        
        print(f"✅ Rôle '{sales_manager_role.name}' assigné à l'utilisateur")
        print(f"✅ Permission '{permission.name}' accordée au rôle")
        
        # Tester l'accès
        if headers:
            response = requests.get(f"{base_url}/api/sales/orders/", headers=headers)
            print(f"GET /api/sales/orders/ - Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Accès autorisé !")
                data = response.json()
                print(f"   Nombre de commandes: {data.get('count', 'N/A')}")
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
        # Orders
        ('GET', '/api/sales/orders/', 'sales_orders_view', 'Lister les commandes'),
        ('POST', '/api/sales/orders/', 'sales_orders_create', 'Créer une commande'),
        ('GET', '/api/sales/orders/1/', 'sales_orders_view', 'Voir une commande'),
        ('PUT', '/api/sales/orders/1/', 'sales_orders_create', 'Modifier une commande'),
        ('DELETE', '/api/sales/orders/1/', 'sales_orders_create', 'Supprimer une commande'),
        ('GET', '/api/sales/orders/pending/', 'sales_orders_view', 'Commandes en attente'),
        ('GET', '/api/sales/orders/confirmed/', 'sales_orders_view', 'Commandes confirmées'),
        ('GET', '/api/sales/orders/shipped/', 'sales_orders_view', 'Commandes expédiées'),
        ('GET', '/api/sales/orders/delivered/', 'sales_orders_view', 'Commandes livrées'),
        ('GET', '/api/sales/orders/cancelled/', 'sales_orders_view', 'Commandes annulées'),
        ('GET', '/api/sales/orders/summary/', 'sales_orders_view', 'Résumé des commandes'),
        
        # Order Items
        ('GET', '/api/sales/order-items/', 'sales_orders_view', 'Lister les articles'),
        ('POST', '/api/sales/order-items/', 'sales_orders_create', 'Créer un article'),
        ('GET', '/api/sales/order-items/1/', 'sales_orders_view', 'Voir un article'),
        ('PUT', '/api/sales/order-items/1/', 'sales_orders_create', 'Modifier un article'),
        ('DELETE', '/api/sales/order-items/1/', 'sales_orders_create', 'Supprimer un article'),
        
        # Invoices
        ('GET', '/api/sales/invoices/', 'sales_invoices_view', 'Lister les factures'),
        ('POST', '/api/sales/invoices/', 'sales_invoices_create', 'Créer une facture'),
        ('GET', '/api/sales/invoices/1/', 'sales_invoices_view', 'Voir une facture'),
        ('PUT', '/api/sales/invoices/1/', 'sales_invoices_create', 'Modifier une facture'),
        ('DELETE', '/api/sales/invoices/1/', 'sales_invoices_create', 'Supprimer une facture'),
        ('GET', '/api/sales/invoices/draft/', 'sales_invoices_view', 'Factures en brouillon'),
        ('GET', '/api/sales/invoices/sent/', 'sales_invoices_view', 'Factures envoyées'),
        ('GET', '/api/sales/invoices/paid/', 'sales_invoices_view', 'Factures payées'),
        ('GET', '/api/sales/invoices/overdue/', 'sales_invoices_view', 'Factures en retard'),
        ('GET', '/api/sales/invoices/summary/', 'sales_invoices_view', 'Résumé des factures'),
        
        # Proforma Invoices
        ('GET', '/api/sales/proformas/', 'sales_proformas_view', 'Lister les devis'),
        ('POST', '/api/sales/proformas/', 'sales_proformas_create', 'Créer un devis'),
        ('GET', '/api/sales/proformas/1/', 'sales_proformas_view', 'Voir un devis'),
        ('PUT', '/api/sales/proformas/1/', 'sales_proformas_create', 'Modifier un devis'),
        ('DELETE', '/api/sales/proformas/1/', 'sales_proformas_create', 'Supprimer un devis'),
        ('GET', '/api/sales/proformas/summary/', 'sales_proformas_view', 'Résumé des devis'),
        
        # Payments
        ('GET', '/api/sales/payments/', 'sales_payments_view', 'Lister les paiements'),
        ('POST', '/api/sales/payments/', 'sales_payments_create', 'Créer un paiement'),
        ('GET', '/api/sales/payments/1/', 'sales_payments_view', 'Voir un paiement'),
        ('PUT', '/api/sales/payments/1/', 'sales_payments_create', 'Modifier un paiement'),
        ('DELETE', '/api/sales/payments/1/', 'sales_payments_create', 'Supprimer un paiement'),
        ('GET', '/api/sales/payments/summary/', 'sales_payments_view', 'Résumé des paiements'),
    ]
    
    for method, endpoint, required_permission, description in actions:
        try:
            if method == 'GET':
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == 'POST':
                # Données de test appropriées selon l'endpoint
                if 'orders' in endpoint:
                    data = {'customer': 1, 'order_date': '2024-01-01', 'status': 'pending'}
                elif 'order-items' in endpoint:
                    data = {'order': 1, 'product': 1, 'quantity': 2, 'unit_price': 100.00}
                elif 'invoices' in endpoint:
                    data = {'order': 1, 'invoice_date': '2024-01-01', 'due_date': '2024-01-31'}
                elif 'proformas' in endpoint:
                    data = {'customer': 1, 'proforma_date': '2024-01-01', 'valid_until': '2024-01-31'}
                elif 'payments' in endpoint:
                    data = {'invoice': 1, 'amount': 100.00, 'payment_method': 'cash'}
                else:
                    data = {}
                response = requests.post(f"{base_url}{endpoint}", json=data, headers=headers)
            elif method == 'PUT':
                data = {'status': 'confirmed'} if 'orders' in endpoint else {'amount': 200.00}
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
        ('sales_orders_view', 'Voir les commandes'),
        ('sales_orders_create', 'Créer des commandes'),
        ('sales_invoices_view', 'Voir les factures'),
        ('sales_invoices_create', 'Créer des factures'),
        ('sales_proformas_view', 'Voir les devis'),
        ('sales_proformas_create', 'Créer des devis'),
        ('sales_payments_view', 'Voir les paiements'),
        ('sales_payments_create', 'Créer des paiements'),
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
            'sales_orders_view', 'sales_orders_create',
            'sales_invoices_view', 'sales_invoices_create',
            'sales_proformas_view', 'sales_proformas_create',
            'sales_payments_view', 'sales_payments_create'
        ]
        
        for perm_codename in permissions_to_assign:
            permission = Permission.objects.get(codename=perm_codename)
            role_permission, created = RolePermission.objects.get_or_create(
                role=sales_manager_role,
                permission=permission,
                defaults={'granted': True}
            )
            if created:
                print(f"✅ Permission '{perm_codename}' assignée au rôle")
        
        # Tester la création d'une commande
        if headers:
            order_data = {
                'customer': 1,
                'order_date': '2024-01-01',
                'status': 'pending',
                'notes': 'Test de création'
            }
            
            response = requests.post(f"{base_url}/api/sales/orders/", 
                                   json=order_data, headers=headers)
            print(f"POST /api/sales/orders/ - Status: {response.status_code}")
            
            if response.status_code == 201:
                print("✅ Commande créée avec succès !")
            elif response.status_code == 400:
                print("⚠️  Erreur de validation (normal si pas de client)")
                print(f"   Détails: {response.json()}")
            else:
                print(f"❌ Erreur inattendue: {response.status_code}")
                print(f"   Réponse: {response.text}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'assignation des permissions: {e}")
    
    print(f"\n" + "=" * 60)
    print("✅ Test de sécurisation de l'API Sales terminé !")
    print("=" * 60)
    
    # Résumé des permissions requises
    print(f"\n📋 RÉSUMÉ DES PERMISSIONS REQUISES:")
    print("-" * 40)
    print("• sales_orders_view - Voir les commandes")
    print("• sales_orders_create - Créer/modifier/supprimer les commandes")
    print("• sales_invoices_view - Voir les factures")
    print("• sales_invoices_create - Créer/modifier/supprimer les factures")
    print("• sales_proformas_view - Voir les devis")
    print("• sales_proformas_create - Créer/modifier/supprimer les devis")
    print("• sales_payments_view - Voir les paiements")
    print("• sales_payments_create - Créer/modifier/supprimer les paiements")

if __name__ == "__main__":
    try:
        test_sales_security()
    except Exception as e:
        print(f"❌ ERREUR lors du test: {e}")
        sys.exit(1)
