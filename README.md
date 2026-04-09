# Nodus CRM-ERP

Système de gestion CRM-ERP développé avec Django.

## Structure du projet

```
nodus/
├── manage.py                  # Script principal pour gérer le projet
├── requirements.txt           # Dépendances Python
├── nodus/
│   ├── __init__.py
│   ├── settings/              # Configuration par environnement
│   │   ├── __init__.py
│   │   ├── base.py            # Paramètres communs
│   │   ├── local.py           # Configuration développement
│   │   └── production.py      # Configuration production
│   ├── urls.py                # Routes globales
│   └── wsgi.py
├── apps/                      # Applications Django
│   ├── __init__.py
│   ├── common/                # Utilitaires partagés
│   ├── customers/             # Gestion des clients
│   ├── inventory/             # Produits et stock
│   ├── stock/                 # Mouvements de stock
│   └── sales/                 # Ventes et facturation
├── static/                    # Fichiers statiques
├── media/                     # Fichiers uploadés
└── templates/                 # Templates HTML
```

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

2. Configurer l'environnement :
```bash
cp .env.example .env
# Éditer .env selon vos besoins
```

3. Appliquer les migrations :
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

5. Lancer le serveur :
```bash
python manage.py runserver
```

## Applications

- **customers** : Gestion de la clientèle
- **inventory** : Produits et gestion de stock
- **stock** : Mouvements de stock (entrées/sorties)
- **sales** : Ventes, factures et devis
- **common** : Utilitaires et classes partagées
# erp_backend
# erp_backend
# erp_backend
