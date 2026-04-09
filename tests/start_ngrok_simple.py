#!/usr/bin/env python3
"""
Script simple pour démarrer le serveur Django avec Ngrok
SANS toucher à la base de données
"""

import os
import sys
import subprocess
import time
import requests

def get_ngrok_url():
    """Récupère l'URL Ngrok"""
    try:
        response = requests.get("http://localhost:4040/api/tunnels")
        data = response.json()
        if data['tunnels']:
            return data['tunnels'][0]['public_url']
        return None
    except:
        return None

def main():
    """Fonction principale"""
    print("🚀 Démarrage du serveur Django avec Ngrok...")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('manage.py'):
        print("❌ Erreur : manage.py non trouvé. Assurez-vous d'être dans le répertoire du projet.")
        sys.exit(1)
    
    # 1. Démarrer Ngrok en arrière-plan
    print("🌐 Démarrage de Ngrok...")
    ngrok_process = subprocess.Popen([
        "ngrok", "http", "8000", "--log=stdout"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Attendre que Ngrok démarre
    print("⏳ Attente du démarrage de Ngrok...")
    time.sleep(3)
    
    # Récupérer l'URL Ngrok
    ngrok_url = get_ngrok_url()
    if ngrok_url:
        print(f"🌍 URL Ngrok : {ngrok_url}")
        print(f"🔗 URLs disponibles :")
        print(f"   - Admin : {ngrok_url}/admin/")
        print(f"   - Dashboard : {ngrok_url}/api/dashboard/overview/")
        print(f"   - API Auth : {ngrok_url}/api/auth/login/")
        print(f"   - Sales Chart : {ngrok_url}/api/dashboard/sales-chart/")
        print(f"   - Recent Orders : {ngrok_url}/api/dashboard/recent-orders/")
        print(f"   - Recent Invoices : {ngrok_url}/api/dashboard/recent-invoices/")
        print(f"   - Alerts : {ngrok_url}/api/dashboard/alerts/")
    else:
        print("⚠️  Impossible de récupérer l'URL Ngrok")
    
    # 2. Démarrer le serveur Django
    print("🚀 Démarrage du serveur de développement...")
    print("📝 Identifiants de test :")
    print("   - Admin : admin / admin123")
    print("   - User1 : user1 / password123")
    print("   - User2 : user2 / password123")
    print("\n🚀 Serveur démarré ! Appuyez sur Ctrl+C pour arrêter.")
    
    try:
        subprocess.run(["python3", "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        ngrok_process.terminate()
        print("👋 Serveur arrêté. Au revoir !")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur : {e}")
        ngrok_process.terminate()

if __name__ == "__main__":
    main()
