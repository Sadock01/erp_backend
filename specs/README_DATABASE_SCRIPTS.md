# 🗄️ Scripts de Base de Données - Baobab ERP

## 📋 Vue d'ensemble

Ce dossier contient des scripts pour gérer la base de données de l'ERP Baobab, incluant le remplissage avec des données de test et les tests des APIs dashboard.

---

## 🚀 Scripts Disponibles

### 1. `populate_database.py`
**Script principal de remplissage de la base de données**

Génère des données de test complètes pour tous les modules :
- 👥 Utilisateurs et rôles
- 👤 Clients
- 📦 Produits et catégories
- 📋 Commandes et factures
- 📦 Mouvements de stock
- 🚨 Alertes

**Utilisation :**
```bash
python3 populate_database.py
```

### 2. `reset_database.py`
**Script de réinitialisation de la base de données**

Vide complètement la base de données et la recrée :
- Supprime la base SQLite existante
- Recrée les migrations
- Applique les migrations
- Crée un super utilisateur

**Utilisation :**
```bash
python3 reset_database.py
```

### 3. `quick_test.py`
**Script de test rapide des APIs**

Teste rapidement tous les endpoints du dashboard :
- Vérifie la connectivité
- Teste chaque API
- Affiche les résultats

**Utilisation :**
```bash
python3 quick_test.py
```

### 4. `test_dashboard_apis.py`
**Script de test complet avec serveur**

Teste les APIs via HTTP (nécessite le serveur Django en cours d'exécution) :
- Authentification
- Tests de tous les endpoints
- Affichage des réponses JSON

**Utilisation :**
```bash
# Dans un terminal : démarrer le serveur
python3 manage.py runserver

# Dans un autre terminal : exécuter les tests
python3 test_dashboard_apis.py
```

---

## 🔧 Installation et Configuration

### Prérequis
- Python 3.8+
- Django 4.2+
- Toutes les dépendances installées

### Configuration de l'environnement
```bash
# Activer l'environnement virtuel (si applicable)
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

---

## 📊 Données Générées

### Utilisateurs de Test
| Username | Mot de passe | Rôle | Description |
|----------|--------------|------|-------------|
| `admin` | `admin123` | Super Admin | Accès complet |
| `manager` | `password123` | Manager | Gestionnaire |
| `sales1` | `password123` | Sales | Commercial |
| `sales2` | `password123` | Sales | Commercial |
| `stock1` | `password123` | Stock Manager | Gestionnaire stock |
| `viewer` | `password123` | Viewer | Consultation seule |

### Données Générées
- **10 clients** avec informations complètes
- **15 produits** dans 5 catégories
- **100 commandes** avec statuts variés
- **~80 factures** avec paiements
- **80 mouvements de stock** (entrées/sorties)
- **Alertes de stock** automatiques
- **Données sur 6 mois** pour les graphiques

---

## 🎯 Workflow Recommandé

### 1. Première Installation
```bash
# 1. Réinitialiser la base de données
python3 reset_database.py

# 2. Remplir avec des données de test
python3 populate_database.py

# 3. Démarrer le serveur
python3 manage.py runserver

# 4. Tester les APIs (dans un autre terminal)
python3 test_dashboard_apis.py
```

### 2. Test Rapide
```bash
# Test sans serveur
python3 quick_test.py
```

### 3. Nouveau Remplissage
```bash
# Si vous voulez regénérer les données
python3 reset_database.py
python3 populate_database.py
```

---

## 🔍 Vérification des Données

### Via l'Interface Admin
1. Démarrer le serveur : `python3 manage.py runserver`
2. Aller sur : http://localhost:8000/admin/
3. Se connecter avec : `admin` / `admin123`
4. Explorer les données dans chaque section

### Via les APIs
```bash
# Tester l'endpoint principal
curl -H "Authorization: Token <token>" \
     http://localhost:8000/api/dashboard/

# Tester les KPIs
curl -H "Authorization: Token <token>" \
     http://localhost:8000/api/dashboard/kpis/
```

---

## 🐛 Dépannage

### Erreur "Module not found"
```bash
# Vérifier que Django est installé
pip install django

# Vérifier l'environnement virtuel
which python3
```

### Erreur de base de données
```bash
# Supprimer manuellement la base
rm db.sqlite3

# Recréer les migrations
python3 manage.py makemigrations
python3 manage.py migrate
```

### Erreur de permissions
```bash
# Vérifier les permissions d'écriture
ls -la db.sqlite3
chmod 664 db.sqlite3
```

---

## 📈 Personnalisation

### Modifier les Données Générées
Éditez `populate_database.py` pour :
- Changer le nombre d'éléments générés
- Modifier les noms des produits/clients
- Ajuster les prix et quantités
- Changer les périodes de données

### Ajouter de Nouveaux Types de Données
1. Créer une nouvelle fonction dans `populate_database.py`
2. L'appeler dans la fonction `main()`
3. Suivre le même pattern que les autres fonctions

---

## 🎉 Résultat Attendu

Après exécution des scripts, vous devriez avoir :
- ✅ Une base de données complètement fonctionnelle
- ✅ Des données réalistes pour tester le dashboard
- ✅ Tous les endpoints API opérationnels
- ✅ Des graphiques avec des données visibles
- ✅ Des alertes et notifications

**Le dashboard sera maintenant entièrement fonctionnel avec des données de test !** 🚀
