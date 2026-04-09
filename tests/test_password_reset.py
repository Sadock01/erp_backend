#!/usr/bin/env python3
"""
Script de test pour les APIs de reset de mot de passe
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "test@example.com"
NEW_PASSWORD = "nouveau_mot_de_passe_123"

def test_password_reset():
    """Test complet du processus de reset de mot de passe"""
    
    print("🔐 Test des APIs de Reset de Mot de Passe")
    print("=" * 50)
    
    # 1. Demande de reset
    print("\n1. Demande de reset de mot de passe...")
    reset_request_data = {
        "email": EMAIL
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset-request/",
            json=reset_request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Demande de reset réussie")
            print("📧 Vérifiez le terminal du serveur pour le code de vérification")
            
            # Attendre que l'utilisateur entre le code
            print("\n⏳ Entrez le code affiché dans le terminal du serveur...")
            code = input("Code de vérification: ").strip()
            
            if code:
                # 2. Confirmation du reset
                print(f"\n2. Confirmation du reset avec le code: {code}")
                reset_confirm_data = {
                    "email": EMAIL,
                    "code": code,
                    "new_password": NEW_PASSWORD,
                    "new_password_confirm": NEW_PASSWORD
                }
                
                response = requests.post(
                    f"{BASE_URL}/api/auth/password-reset-confirm/",
                    json=reset_confirm_data,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Status Code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
                
                if response.status_code == 200:
                    print("✅ Reset de mot de passe réussi!")
                    print("🔑 Vérifiez le terminal du serveur pour la confirmation")
                else:
                    print("❌ Erreur lors de la confirmation du reset")
            else:
                print("❌ Code non fourni")
        else:
            print("❌ Erreur lors de la demande de reset")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion. Assurez-vous que le serveur Django est démarré.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_invalid_code():
    """Test avec un code invalide"""
    
    print("\n\n🧪 Test avec code invalide")
    print("=" * 30)
    
    reset_confirm_data = {
        "email": EMAIL,
        "code": "000000",  # Code invalide
        "new_password": NEW_PASSWORD,
        "new_password_confirm": NEW_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset-confirm/",
            json=reset_confirm_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion. Assurez-vous que le serveur Django est démarré.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

def test_validation_errors():
    """Test des erreurs de validation"""
    
    print("\n\n🧪 Test des erreurs de validation")
    print("=" * 35)
    
    # Test avec mots de passe différents
    print("\n1. Test avec mots de passe différents...")
    reset_confirm_data = {
        "email": EMAIL,
        "code": "123456",
        "new_password": "mot_de_passe_1",
        "new_password_confirm": "mot_de_passe_2"  # Différent
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/password-reset-confirm/",
            json=reset_confirm_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion. Assurez-vous que le serveur Django est démarré.")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Démarrage des tests de reset de mot de passe")
    print("=" * 50)
    
    # Test principal
    test_password_reset()
    
    # Tests d'erreurs
    test_invalid_code()
    test_validation_errors()
    
    print("\n✅ Tests terminés!")
    print("\n📋 Instructions:")
    print("1. Démarrez le serveur Django: python3 manage.py runserver")
    print("2. Exécutez ce script: python3 test_password_reset.py")
    print("3. Suivez les instructions à l'écran")
    print("4. Vérifiez les messages dans le terminal du serveur")
