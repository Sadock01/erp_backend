#!/usr/bin/env python3
"""
Script pour démarrer le serveur Django avec Ngrok
"""

import os
import sys
import subprocess
import time
import requests
import json

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} terminé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False

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
    
    # 1. Appliquer les migrations
    if not run_command("python3 manage.py makemigrations", "Création des migrations"):
        sys.exit(1)
    
    if not run_command("python3 manage.py migrate", "Application des migrations"):
        sys.exit(1)
    
    # 2. Créer un superutilisateur si nécessaire
    print("🔐 Vérification du superutilisateur...")
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("👤 Création du superutilisateur...")
            subprocess.run([
                "python3", "manage.py", "createsuperuser",
                "--username", "admin",
                "--email", "admin@test.com",
                "--noinput"
            ], check=True)
            # Définir le mot de passe
            subprocess.run([
                "python3", "manage.py", "shell", "-c",
                "from django.contrib.auth.models import User; u = User.objects.get(username='admin'); u.set_password('admin123'); u.save()"
            ], check=True)
            print("✅ Superutilisateur créé (admin/admin123)")
        else:
            print("✅ Superutilisateur existe déjà")
    except Exception as e:
        print(f"⚠️  Erreur lors de la création du superutilisateur : {e}")
    
    # 3. Remplir la base de données avec des données de test
    print("📊 Remplissage de la base de données...")
    if not run_command("python3 populate_dashboard_test_data.py", "Population des données de test"):
        print("⚠️  Erreur lors du remplissage, mais on continue...")
    
    # 4. Démarrer Ngrok en arrière-plan
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
    
    # 5. Démarrer le serveur Django
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
