#!/usr/bin/env python3
"""
Script de test pour les APIs Alertes et Notifications
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from apps.common.models import Alert, Notification

def test_alerts_apis():
    """Tester les APIs d'alertes"""
    print("🔔 Test des APIs Alertes")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # 1. Créer des données de test
    print("📝 Création des données de test...")
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Créer des alertes de test
    alerts_data = [
        {
            'title': 'Stock bas - iPhone 15',
            'message': 'Le stock de iPhone 15 est en dessous du seuil critique (5 unités restantes)',
            'alert_type': 'stock_low',
            'priority': 'high',
            'user': user,
            'action_url': '/inventory/products/1/',
            'action_label': 'Voir le produit'
        },
        {
            'title': 'Facture en retard',
            'message': 'La facture INV-000001 est en retard de 5 jours',
            'alert_type': 'invoice_overdue',
            'priority': 'critical',
            'user': user,
            'action_url': '/sales/invoices/1/',
            'action_label': 'Voir la facture'
        },
        {
            'title': 'Commande en attente',
            'message': 'La commande ORD-000001 attend validation depuis 2 heures',
            'alert_type': 'order_pending',
            'priority': 'medium',
            'user': user,
            'action_url': '/sales/orders/1/',
            'action_label': 'Valider'
        }
    ]
    
    for alert_data in alerts_data:
        Alert.objects.get_or_create(
            title=alert_data['title'],
            defaults=alert_data
        )
    
    print(f"✅ {len(alerts_data)} alertes créées")
    
    # 2. Tester l'API de liste des alertes
    print("\n📋 Test GET /api/alerts/")
    try:
        response = requests.get(f"{base_url}/alerts/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Nombre d'alertes: {len(data.get('data', []))}")
            print(f"✅ Résumé: {data.get('summary', {})}")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # 3. Tester l'API de création d'alerte
    print("\n➕ Test POST /api/alerts/create/")
    try:
        new_alert = {
            'title': 'Test API Alerte',
            'message': 'Ceci est un test de création d\'alerte via API',
            'alert_type': 'custom',
            'priority': 'low',
            'user': user.id,
            'action_url': '/test/',
            'action_label': 'Tester'
        }
        
        response = requests.post(
            f"{base_url}/alerts/create/",
            json=new_alert,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Alerte créée: {data.get('data', {}).get('title')}")
            alert_id = data.get('data', {}).get('id')
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            alert_id = None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        alert_id = None
    
    # 4. Tester l'API de marquage comme lue
    if alert_id:
        print(f"\n👁️ Test PATCH /api/alerts/{alert_id}/mark-read/")
        try:
            response = requests.patch(f"{base_url}/alerts/{alert_id}/mark-read/")
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"✅ Alerte marquée comme lue")
            else:
                print(f"❌ Erreur: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")


def test_notifications_apis():
    """Tester les APIs de notifications"""
    print("\n🔔 Test des APIs Notifications")
    print("=" * 50)
    
    base_url = "http://localhost:8000/api"
    
    # 1. Créer des données de test
    print("📝 Création des données de test...")
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Créer des notifications de test
    notifications_data = [
        {
            'title': 'Nouvelle commande',
            'message': 'Une nouvelle commande ORD-000001 a été créée par Jean Dupont',
            'notification_type': 'order_created',
            'priority': 'medium',
            'user': user,
            'action_url': '/sales/orders/1/',
            'action_label': 'Voir la commande'
        },
        {
            'title': 'Paiement reçu',
            'message': 'Un paiement de 150,000 FCFA a été reçu pour la facture INV-000001',
            'notification_type': 'payment_received',
            'priority': 'high',
            'user': user,
            'action_url': '/sales/payments/1/',
            'action_label': 'Voir le paiement'
        },
        {
            'title': 'Rappel de maintenance',
            'message': 'La maintenance programmée aura lieu demain à 2h00',
            'notification_type': 'reminder',
            'priority': 'low',
            'user': user,
            'action_url': '/maintenance/',
            'action_label': 'Voir les détails'
        }
    ]
    
    for notification_data in notifications_data:
        Notification.objects.get_or_create(
            title=notification_data['title'],
            defaults=notification_data
        )
    
    print(f"✅ {len(notifications_data)} notifications créées")
    
    # 2. Tester l'API de liste des notifications
    print("\n📋 Test GET /api/notifications/")
    try:
        response = requests.get(f"{base_url}/notifications/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Nombre de notifications: {len(data.get('data', []))}")
            print(f"✅ Résumé: {data.get('summary', {})}")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
    
    # 3. Tester l'API de création de notification
    print("\n➕ Test POST /api/notifications/create/")
    try:
        new_notification = {
            'title': 'Test API Notification',
            'message': 'Ceci est un test de création de notification via API',
            'notification_type': 'custom',
            'priority': 'low',
            'user': user.id,
            'action_url': '/test/',
            'action_label': 'Tester'
        }
        
        response = requests.post(
            f"{base_url}/notifications/create/",
            json=new_notification,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"✅ Notification créée: {data.get('data', {}).get('title')}")
            notification_id = data.get('data', {}).get('id')
        else:
            print(f"❌ Erreur: {response.status_code} - {response.text}")
            notification_id = None
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        notification_id = None
    
    # 4. Tester l'API de marquage comme lue
    if notification_id:
        print(f"\n👁️ Test PATCH /api/notifications/{notification_id}/mark-read/")
        try:
            response = requests.patch(f"{base_url}/notifications/{notification_id}/mark-read/")
            if response.status_code == 200:
                print(f"✅ Status: {response.status_code}")
                print(f"✅ Notification marquée comme lue")
            else:
                print(f"❌ Erreur: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Erreur de connexion: {e}")


def main():
    """Fonction principale"""
    print("🚀 Test des APIs Alertes et Notifications")
    print("=" * 60)
    
    # Vérifier que le serveur Django est démarré
    try:
        response = requests.get("http://localhost:8000/api/alerts/", timeout=5)
        print("✅ Serveur Django détecté")
    except:
        print("❌ Serveur Django non détecté. Démarrez le serveur avec:")
        print("   python3 manage.py runserver")
        return
    
    # Tester les APIs
    test_alerts_apis()
    test_notifications_apis()
    
    print("\n🎉 Tests terminés !")
    print("\n📚 URLs disponibles:")
    print("   - Alertes: http://localhost:8000/api/alerts/")
    print("   - Notifications: http://localhost:8000/api/notifications/")
    print("   - Admin: http://localhost:8000/admin/")


if __name__ == "__main__":
    main()

