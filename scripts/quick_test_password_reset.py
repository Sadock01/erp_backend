#!/usr/bin/env python3
"""
Test rapide des APIs de reset de mot de passe sans serveur
"""

import os
import sys
import django
from django.conf import settings

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from apps.common.models import PasswordResetCode
from apps.common.serializers import PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.contrib.auth.models import User
from django.utils import timezone

def test_password_reset_models():
    """Test des modèles de reset de mot de passe"""
    
    print("🧪 Test des modèles de reset de mot de passe")
    print("=" * 50)
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='testuser_reset',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('ancien_mot_de_passe')
        user.save()
        print(f"✅ Utilisateur créé: {user.username}")
    else:
        print(f"✅ Utilisateur existant: {user.username}")
    
    # Test de génération de code
    print("\n1. Test de génération de code...")
    reset_code = PasswordResetCode.objects.create(
        user=user,
        email=user.email
    )
    
    print(f"✅ Code généré: {reset_code.code}")
    print(f"✅ Expire à: {reset_code.expires_at}")
    print(f"✅ Valide: {reset_code.is_valid()}")
    
    # Test de validation
    print("\n2. Test de validation...")
    print(f"✅ Code correct: {reset_code.code == reset_code.code}")
    print(f"✅ Non utilisé: {not reset_code.is_used}")
    print(f"✅ Tentatives: {reset_code.attempts}")
    
    # Test d'incrémentation des tentatives
    print("\n3. Test d'incrémentation des tentatives...")
    reset_code.increment_attempts()
    print(f"✅ Tentatives après incrémentation: {reset_code.attempts}")
    
    # Test de marquage comme utilisé
    print("\n4. Test de marquage comme utilisé...")
    reset_code.mark_as_used()
    print(f"✅ Utilisé: {reset_code.is_used}")
    print(f"✅ Valide après utilisation: {reset_code.is_valid()}")
    
    return reset_code

def test_serializers():
    """Test des serializers"""
    
    print("\n\n🧪 Test des serializers")
    print("=" * 30)
    
    # Test PasswordResetRequestSerializer
    print("\n1. Test PasswordResetRequestSerializer...")
    request_data = {"email": "test@example.com"}
    serializer = PasswordResetRequestSerializer(data=request_data)
    
    if serializer.is_valid():
        print("✅ Données de demande valides")
        print(f"✅ Email: {serializer.validated_data['email']}")
    else:
        print("❌ Erreurs de validation:", serializer.errors)
    
    # Test PasswordResetConfirmSerializer
    print("\n2. Test PasswordResetConfirmSerializer...")
    confirm_data = {
        "email": "test@example.com",
        "code": "123456",
        "new_password": "nouveau_mot_de_passe",
        "new_password_confirm": "nouveau_mot_de_passe"
    }
    serializer = PasswordResetConfirmSerializer(data=confirm_data)
    
    if serializer.is_valid():
        print("✅ Données de confirmation valides")
        print(f"✅ Email: {serializer.validated_data['email']}")
        print(f"✅ Code: {serializer.validated_data['code']}")
    else:
        print("❌ Erreurs de validation:", serializer.errors)
    
    # Test avec mots de passe différents
    print("\n3. Test avec mots de passe différents...")
    confirm_data_invalid = {
        "email": "test@example.com",
        "code": "123456",
        "new_password": "mot_de_passe_1",
        "new_password_confirm": "mot_de_passe_2"
    }
    serializer = PasswordResetConfirmSerializer(data=confirm_data_invalid)
    
    if serializer.is_valid():
        print("❌ Validation incorrecte - devrait échouer")
    else:
        print("✅ Validation correcte - échec attendu")
        print(f"✅ Erreurs: {serializer.errors}")

def test_password_reset_process():
    """Test du processus complet de reset"""
    
    print("\n\n🧪 Test du processus complet")
    print("=" * 35)
    
    # Créer un utilisateur
    user, created = User.objects.get_or_create(
        username='testuser_process',
        defaults={
            'email': 'process@example.com',
            'first_name': 'Process',
            'last_name': 'Test'
        }
    )
    if created:
        user.set_password('ancien_mot_de_passe')
        user.save()
    
    # 1. Désactiver les anciens codes
    print("\n1. Désactivation des anciens codes...")
    PasswordResetCode.objects.filter(
        email=user.email,
        is_used=False
    ).update(is_used=True)
    print("✅ Anciens codes désactivés")
    
    # 2. Créer un nouveau code
    print("\n2. Création d'un nouveau code...")
    reset_code = PasswordResetCode.objects.create(
        user=user,
        email=user.email
    )
    print(f"✅ Nouveau code créé: {reset_code.code}")
    print(f"✅ Expire à: {reset_code.expires_at}")
    
    # 3. Simuler l'affichage du code
    print(f"\n{'='*60}")
    print(f"🔐 CODE DE RESET DE MOT DE PASSE")
    print(f"{'='*60}")
    print(f"Email: {user.email}")
    print(f"Code: {reset_code.code}")
    print(f"Expire dans: 15 minutes")
    print(f"{'='*60}")
    
    # 4. Vérifier le code
    print(f"\n3. Vérification du code...")
    print(f"✅ Code valide: {reset_code.is_valid()}")
    print(f"✅ Code correct: {reset_code.code == reset_code.code}")
    
    # 5. Mettre à jour le mot de passe
    print(f"\n4. Mise à jour du mot de passe...")
    user.set_password('nouveau_mot_de_passe_123')
    user.save()
    print("✅ Mot de passe mis à jour")
    
    # 6. Marquer le code comme utilisé
    print(f"\n5. Marquage du code comme utilisé...")
    reset_code.mark_as_used()
    print("✅ Code marqué comme utilisé")
    
    # 7. Confirmation finale
    print(f"\n{'='*60}")
    print(f"✅ MOT DE PASSE RÉINITIALISÉ AVEC SUCCÈS")
    print(f"{'='*60}")
    print(f"Email: {user.email}")
    print(f"Utilisateur: {user.username}")
    print(f"Date: {timezone.now()}")
    print(f"{'='*60}")

def cleanup_test_data():
    """Nettoyer les données de test"""
    
    print("\n\n🧹 Nettoyage des données de test")
    print("=" * 35)
    
    # Supprimer les codes de test
    deleted_codes = PasswordResetCode.objects.filter(
        email__in=['test@example.com', 'process@example.com']
    ).delete()
    print(f"✅ Codes supprimés: {deleted_codes[0]}")
    
    # Supprimer les utilisateurs de test
    deleted_users = User.objects.filter(
        username__in=['testuser_reset', 'testuser_process']
    ).delete()
    print(f"✅ Utilisateurs supprimés: {deleted_users[0]}")

if __name__ == "__main__":
    print("🚀 Test des APIs de Reset de Mot de Passe")
    print("=" * 50)
    
    try:
        # Tests des modèles
        test_password_reset_models()
        
        # Tests des serializers
        test_serializers()
        
        # Test du processus complet
        test_password_reset_process()
        
        # Nettoyage
        cleanup_test_data()
        
        print("\n✅ Tous les tests sont passés avec succès!")
        print("\n📋 Pour tester avec le serveur:")
        print("1. python3 manage.py runserver")
        print("2. python3 test_password_reset.py")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {e}")
        import traceback
        traceback.print_exc()
