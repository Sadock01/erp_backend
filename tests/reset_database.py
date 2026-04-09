#!/usr/bin/env python3
"""
Script pour vider et recréer la base de données Nodus ERP
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from django.core.management import execute_from_command_line

def reset_database():
    """Vider et recréer la base de données"""
    print("🗑️  Suppression de la base de données existante...")
    
    # Supprimer le fichier de base de données SQLite
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        os.remove(db_path)
        print("✅ Base de données supprimée")
    
    print("\n🔄 Création des migrations...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    print("\n📦 Application des migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("\n👤 Création du super utilisateur...")
    execute_from_command_line(['manage.py', 'createsuperuser', '--noinput', '--username', 'admin', '--email', 'admin@baobab-erp.com'])
    
    # Définir le mot de passe pour le super utilisateur
    from django.contrib.auth.models import User
    admin_user = User.objects.get(username='admin')
    admin_user.set_password('admin123')
    admin_user.save()
    
    print("✅ Super utilisateur 'admin' créé avec le mot de passe 'admin123'")
    
    print("\n🎉 Base de données réinitialisée avec succès !")
    print("Vous pouvez maintenant exécuter : python3 populate_database.py")

if __name__ == "__main__":
    reset_database()
