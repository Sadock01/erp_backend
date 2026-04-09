#!/usr/bin/env python3
"""
Script de démarrage rapide avec données de test
"""

import subprocess
import sys
import time
import os

def run_command(command, description):
    """Exécuter une commande et afficher le résultat"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Succès")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erreur")
        print(f"Code de sortie: {e.returncode}")
        if e.stdout:
            print(f"Sortie: {e.stdout}")
        if e.stderr:
            print(f"Erreur: {e.stderr}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Démarrage rapide de Baobab ERP avec données de test")
    print("=" * 60)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not os.path.exists('manage.py'):
        print("❌ Erreur: manage.py non trouvé. Exécutez ce script depuis la racine du projet.")
        sys.exit(1)
    
    # 1. Réinitialiser la base de données
    if not run_command("python3 reset_database.py", "Réinitialisation de la base de données"):
        print("❌ Impossible de réinitialiser la base de données")
        sys.exit(1)
    
    # 2. Remplir avec des données de test
    if not run_command("python3 populate_database.py", "Remplissage avec des données de test"):
        print("❌ Impossible de remplir la base de données")
        sys.exit(1)
    
    # 3. Test rapide
    print("\n🧪 Test rapide des APIs...")
    if run_command("python3 quick_test.py", "Test des APIs"):
        print("✅ Tous les tests sont passés !")
    else:
        print("⚠️  Certains tests ont échoué, mais le serveur peut quand même fonctionner")
    
    print("\n" + "=" * 60)
    print("🎉 Configuration terminée !")
    print("=" * 60)
    
    print("\n📋 Prochaines étapes :")
    print("1. Démarrer le serveur : python3 manage.py runserver")
    print("2. Ouvrir l'admin : http://localhost:8000/admin/")
    print("   - Utilisateur : admin")
    print("   - Mot de passe : admin123")
    print("3. Tester les APIs : python3 test_dashboard_apis.py")
    print("4. Accéder au dashboard : http://localhost:8000/api/dashboard/")
    
    print("\n🔑 Comptes de test disponibles :")
    print("   admin / admin123 (Super Admin)")
    print("   manager / password123 (Manager)")
    print("   sales1 / password123 (Sales)")
    print("   stock1 / password123 (Stock Manager)")
    print("   viewer / password123 (Viewer)")
    
    print("\n🚀 Pour démarrer le serveur maintenant, exécutez :")
    print("   python3 manage.py runserver")

if __name__ == "__main__":
    main()
