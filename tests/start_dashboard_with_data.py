#!/usr/bin/env python3
"""
Script pour démarrer le serveur avec des données de test pour le dashboard
"""

import os
import sys
import subprocess
import time

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

def main():
    """Fonction principale"""
    print("🚀 Démarrage du serveur avec données de test pour le dashboard...")
    
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
    
    # 4. Démarrer le serveur
    print("🌐 Démarrage du serveur de développement...")
    print("🔗 URLs disponibles :")
    print("   - Admin : http://localhost:8000/admin/")
    print("   - Dashboard : http://localhost:8000/api/dashboard/overview/")
    print("   - API Auth : http://localhost:8000/api/auth/login/")
    print("\n📝 Identifiants de test :")
    print("   - Admin : admin / admin123")
    print("   - User1 : user1 / password123")
    print("   - User2 : user2 / password123")
    print("\n🚀 Serveur démarré ! Appuyez sur Ctrl+C pour arrêter.")
    
    try:
        subprocess.run(["python3", "manage.py", "runserver"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté. Au revoir !")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage du serveur : {e}")

if __name__ == "__main__":
    main()
