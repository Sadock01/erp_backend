#!/usr/bin/env python3
"""
Script de test pour les APIs Dashboard Baobab ERP
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "admin",
    "password": "admin123"
}

def test_dashboard_apis():
    """Test des APIs dashboard"""
    
    print("🚀 Test des APIs Dashboard Baobab ERP")
    print("=" * 50)
    
    # 1. Authentification
    print("\n1. 🔐 Test d'authentification...")
    auth_response = requests.post(f"{BASE_URL}/auth/login/", json=TEST_USER)
    
    if auth_response.status_code == 200:
        token = auth_response.json().get('token')
        headers = {"Authorization": f"Token {token}"}
        print("✅ Authentification réussie")
    else:
        print(f"❌ Échec de l'authentification: {auth_response.status_code}")
        print(auth_response.text)
        return
    
    # 2. Test KPIs
    print("\n2. 📊 Test KPIs...")
    kpis_response = requests.get(f"{BASE_URL}/dashboard/kpis/", headers=headers)
    print(f"Status: {kpis_response.status_code}")
    if kpis_response.status_code == 200:
        print("✅ KPIs récupérés avec succès")
        print(f"Données: {json.dumps(kpis_response.json(), indent=2)}")
    else:
        print(f"❌ Erreur KPIs: {kpis_response.text}")
    
    # 3. Test Graphique des ventes
    print("\n3. 📈 Test graphique des ventes...")
    sales_chart_response = requests.get(f"{BASE_URL}/dashboard/sales-chart/", headers=headers)
    print(f"Status: {sales_chart_response.status_code}")
    if sales_chart_response.status_code == 200:
        print("✅ Graphique des ventes récupéré avec succès")
    else:
        print(f"❌ Erreur graphique des ventes: {sales_chart_response.text}")
    
    # 4. Test Top produits
    print("\n4. 🏆 Test top produits...")
    products_chart_response = requests.get(f"{BASE_URL}/dashboard/products-chart/", headers=headers)
    print(f"Status: {products_chart_response.status_code}")
    if products_chart_response.status_code == 200:
        print("✅ Top produits récupéré avec succès")
    else:
        print(f"❌ Erreur top produits: {products_chart_response.text}")
    
    # 5. Test Répartition clients
    print("\n5. 👥 Test répartition clients...")
    clients_chart_response = requests.get(f"{BASE_URL}/dashboard/clients-chart/", headers=headers)
    print(f"Status: {clients_chart_response.status_code}")
    if clients_chart_response.status_code == 200:
        print("✅ Répartition clients récupérée avec succès")
    else:
        print(f"❌ Erreur répartition clients: {clients_chart_response.text}")
    
    # 6. Test Alertes
    print("\n6. 🚨 Test alertes...")
    alerts_response = requests.get(f"{BASE_URL}/dashboard/alerts/", headers=headers)
    print(f"Status: {alerts_response.status_code}")
    if alerts_response.status_code == 200:
        print("✅ Alertes récupérées avec succès")
    else:
        print(f"❌ Erreur alertes: {alerts_response.text}")
    
    # 7. Test Commandes récentes
    print("\n7. 🛒 Test commandes récentes...")
    recent_orders_response = requests.get(f"{BASE_URL}/dashboard/recent-orders/", headers=headers)
    print(f"Status: {recent_orders_response.status_code}")
    if recent_orders_response.status_code == 200:
        print("✅ Commandes récentes récupérées avec succès")
    else:
        print(f"❌ Erreur commandes récentes: {recent_orders_response.text}")
    
    # 8. Test Factures récentes
    print("\n8. 💰 Test factures récentes...")
    recent_invoices_response = requests.get(f"{BASE_URL}/dashboard/recent-invoices/", headers=headers)
    print(f"Status: {recent_invoices_response.status_code}")
    if recent_invoices_response.status_code == 200:
        print("✅ Factures récentes récupérées avec succès")
    else:
        print(f"❌ Erreur factures récentes: {recent_invoices_response.text}")
    
    # 9. Test Dashboard complet
    print("\n9. 🎯 Test dashboard complet...")
    dashboard_all_response = requests.get(f"{BASE_URL}/dashboard/", headers=headers)
    print(f"Status: {dashboard_all_response.status_code}")
    if dashboard_all_response.status_code == 200:
        print("✅ Dashboard complet récupéré avec succès")
    else:
        print(f"❌ Erreur dashboard complet: {dashboard_all_response.text}")
    
    # 10. Test APIs de résumé
    print("\n10. 📋 Test APIs de résumé...")
    
    # Résumé commandes
    orders_summary_response = requests.get(f"{BASE_URL}/sales/orders/summary/", headers=headers)
    print(f"Résumé commandes - Status: {orders_summary_response.status_code}")
    if orders_summary_response.status_code == 200:
        print("✅ Résumé commandes récupéré avec succès")
    else:
        print(f"❌ Erreur résumé commandes: {orders_summary_response.text}")
    
    # Résumé factures
    invoices_summary_response = requests.get(f"{BASE_URL}/sales/invoices/summary/", headers=headers)
    print(f"Résumé factures - Status: {invoices_summary_response.status_code}")
    if invoices_summary_response.status_code == 200:
        print("✅ Résumé factures récupéré avec succès")
    else:
        print(f"❌ Erreur résumé factures: {invoices_summary_response.text}")
    
    # Résumé stock
    movements_summary_response = requests.get(f"{BASE_URL}/stock/movements/summary/", headers=headers)
    print(f"Résumé stock - Status: {movements_summary_response.status_code}")
    if movements_summary_response.status_code == 200:
        print("✅ Résumé stock récupéré avec succès")
    else:
        print(f"❌ Erreur résumé stock: {movements_summary_response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests terminés !")
    print("=" * 50)

if __name__ == "__main__":
    test_dashboard_apis()
