# 📋 Vue d'ensemble des APIs - Baobab ERP

## 🎯 Introduction

Le système Baobab ERP propose une architecture API REST complète pour la gestion d'entreprise. Cette documentation présente tous les principaux endpoints disponibles et leurs utilités.

## 🔐 Base URL et Authentification

**Base URL :** `http://localhost:8000/api/`

**Authentification :** Token-based (Django REST Framework)
```
Authorization: Token <votre_token>
```

---

## 📊 Tableau récapitulatif des APIs

| Module | Endpoint | Description | Utilité principale |
|--------|----------|-------------|-------------------|
| **Auth** | `/api/auth/` | Authentification | Gestion des sessions utilisateur |
| **Customers** | `/api/customers/` | Gestion clients | CRM et base de données clients |
| **Inventory** | `/api/inventory/` | Gestion produits | Catalogue et variantes produits |
| **Stock** | `/api/stock/` | Gestion stock | Mouvements et alertes stock |
| **Sales** | `/api/sales/` | Gestion ventes | Commandes, factures, paiements |
| **Permissions** | `/api/permissions/` | Gestion rôles | Contrôle d'accès et permissions |

---

## 🔑 1. API Authentification (`/api/auth/`)

### Utilité
Gestion complète de l'authentification et des sessions utilisateur.

### Endpoints principaux

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `POST` | `/api/auth/login/` | Connexion utilisateur | Authentification et génération token |
| `POST` | `/api/auth/logout/` | Déconnexion | Invalidation du token |
| `GET` | `/api/auth/profile/` | Profil utilisateur | Récupération des infos utilisateur |
| `POST` | `/api/auth/refresh-token/` | Renouvellement token | Sécurité et continuité de session |

### Cas d'usage
- Connexion/déconnexion des utilisateurs
- Gestion des sessions sécurisées
- Récupération du profil utilisateur
- Renouvellement automatique des tokens

---

## 👥 2. API Clients (`/api/customers/`)

### Utilité
Gestion complète de la base de données clients (CRM).

### Endpoints principaux

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/customers/` | Liste tous les clients | Consultation et recherche clients |
| `POST` | `/api/customers/` | Créer un client | Ajout de nouveaux clients |
| `GET` | `/api/customers/{id}/` | Détail client | Fiche détaillée d'un client |
| `PUT/PATCH` | `/api/customers/{id}/` | Modifier client | Mise à jour des informations |
| `DELETE` | `/api/customers/{id}/` | Supprimer client | Désactivation (soft delete) |
| `GET` | `/api/customers/active/` | Clients actifs | Filtrage par statut |
| `GET` | `/api/customers/search/` | Recherche avancée | Recherche multicritères |

### Fonctionnalités avancées
- **Filtrage** : Par pays, entreprise, statut
- **Recherche** : Nom, email, téléphone, entreprise
- **Tri** : Par nom, email, date de création
- **Pagination** : Gestion des grandes listes
- **Soft delete** : Désactivation sans suppression

### Cas d'usage
- Gestion de la base clients
- Recherche et filtrage
- Suivi des informations clients
- Intégration avec les ventes

---

## 📦 3. API Inventaire (`/api/inventory/`)

### Utilité
Gestion complète du catalogue produits et des catégories.

### Endpoints principaux

#### Catégories (`/api/inventory/categories/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/inventory/categories/` | Liste catégories | Organisation des produits |
| `POST` | `/api/inventory/categories/` | Créer catégorie | Structuration du catalogue |
| `GET` | `/api/inventory/categories/active/` | Catégories actives | Filtrage par statut |
| `GET` | `/api/inventory/categories/{id}/products/` | Produits par catégorie | Navigation hiérarchique |

#### Produits (`/api/inventory/products/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/inventory/products/` | Liste produits | Consultation du catalogue |
| `POST` | `/api/inventory/products/` | Créer produit | Ajout de nouveaux produits |
| `GET` | `/api/inventory/products/{id}/` | Détail produit | Fiche technique complète |
| `PUT/PATCH` | `/api/inventory/products/{id}/` | Modifier produit | Mise à jour des informations |
| `DELETE` | `/api/inventory/products/{id}/` | Supprimer produit | Retrait du catalogue |

#### Variantes (`/api/inventory/variants/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/inventory/variants/` | Liste variantes | Gestion des déclinaisons |
| `POST` | `/api/inventory/variants/` | Créer variante | Ajout de nouvelles déclinaisons |
| `GET` | `/api/inventory/variants/{id}/` | Détail variante | Spécifications détaillées |

### Fonctionnalités avancées
- **Filtrage** : Par statut, type, catégorie, prix, stock
- **Recherche** : Nom, description, SKU, code-barres
- **Gestion hiérarchique** : Catégories parentes/enfants
- **Types de produits** : Simple, variable, bundle
- **Gestion des variantes** : Couleur, taille, modèle

### Cas d'usage
- Gestion du catalogue produits
- Organisation par catégories
- Gestion des variantes (couleurs, tailles)
- Intégration avec le stock et les ventes

---

## 📊 4. API Stock (`/api/stock/`)

### Utilité
Gestion complète des mouvements de stock, alertes et rapports.

### Endpoints principaux

#### Mouvements (`/api/stock/movements/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/stock/movements/` | Liste mouvements | Suivi des entrées/sorties |
| `POST` | `/api/stock/movements/` | Créer mouvement | Enregistrement des opérations |
| `GET` | `/api/stock/movements/entries/` | Entrées stock | Suivi des réceptions |
| `GET` | `/api/stock/movements/exits/` | Sorties stock | Suivi des expéditions |
| `GET` | `/api/stock/movements/pending_approval/` | En attente | Validation des mouvements |

#### Ajustements (`/api/stock/adjustments/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/stock/adjustments/` | Liste ajustements | Corrections d'inventaire |
| `POST` | `/api/stock/adjustments/` | Créer ajustement | Correction des écarts |

#### Alertes (`/api/stock/alerts/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/stock/alerts/` | Liste alertes | Surveillance du stock |
| `POST` | `/api/stock/alerts/` | Créer alerte | Configuration des seuils |

#### Rapports (`/api/stock/reports/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/stock/reports/` | Générer rapports | Analyses et statistiques |

### Fonctionnalités avancées
- **Types de mouvements** : Achat, vente, ajustement, transfert
- **Approbation** : Workflow de validation
- **Alertes automatiques** : Seuils de stock bas
- **Rapports** : Analyses et statistiques
- **Traçabilité** : Historique complet des mouvements

### Cas d'usage
- Suivi des mouvements de stock
- Gestion des inventaires
- Alertes de rupture de stock
- Rapports de gestion
- Contrôle des coûts

---

## 💰 5. API Ventes (`/api/sales/`)

### Utilité
Gestion complète du processus de vente : commandes, factures, devis et paiements.

### Endpoints principaux

#### Commandes (`/api/sales/orders/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/sales/orders/` | Liste commandes | Suivi des ventes |
| `POST` | `/api/sales/orders/` | Créer commande | Nouvelle vente |
| `GET` | `/api/sales/orders/pending/` | Commandes en attente | Workflow de validation |
| `GET` | `/api/sales/orders/confirmed/` | Commandes confirmées | Suivi des validations |
| `GET` | `/api/sales/orders/shipped/` | Commandes expédiées | Suivi logistique |
| `GET` | `/api/sales/orders/delivered/` | Commandes livrées | Finalisation des ventes |

#### Articles de commande (`/api/sales/order-items/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/sales/order-items/` | Liste articles | Détail des commandes |
| `POST` | `/api/sales/order-items/` | Créer article | Ajout de produits |
| `PUT/PATCH` | `/api/sales/order-items/{id}/` | Modifier article | Mise à jour des quantités |

#### Factures (`/api/sales/invoices/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/sales/invoices/` | Liste factures | Gestion comptable |
| `POST` | `/api/sales/invoices/` | Créer facture | Facturation des commandes |
| `GET` | `/api/sales/invoices/{id}/pdf/` | PDF facture | Génération de documents |

#### Devis (`/api/sales/proformas/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/sales/proformas/` | Liste devis | Gestion des propositions |
| `POST` | `/api/sales/proformas/` | Créer devis | Proposition commerciale |

#### Paiements (`/api/sales/payments/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/sales/payments/` | Liste paiements | Suivi des encaissements |
| `POST` | `/api/sales/payments/` | Enregistrer paiement | Gestion des règlements |

### Fonctionnalités avancées
- **Workflow complet** : Devis → Commande → Facture → Paiement
- **Statuts** : Pending, confirmed, shipped, delivered, cancelled
- **Calculs automatiques** : Taxes, remises, totaux
- **Génération PDF** : Factures et devis
- **Suivi des paiements** : Échéances et relances

### Cas d'usage
- Processus de vente complet
- Gestion des commandes
- Facturation et devis
- Suivi des paiements
- Rapports de vente

---

## 🔐 6. API Permissions (`/api/permissions/`)

### Utilité
Gestion complète du système de rôles et permissions pour le contrôle d'accès.

### Endpoints principaux

#### Rôles (`/api/permissions/roles/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/permissions/roles/` | Liste rôles | Gestion des rôles |
| `POST` | `/api/permissions/roles/` | Créer rôle | Définition de nouveaux rôles |
| `GET` | `/api/permissions/roles/active/` | Rôles actifs | Filtrage par statut |
| `GET` | `/api/permissions/roles/system/` | Rôles système | Rôles prédéfinis |
| `GET` | `/api/permissions/roles/{id}/permissions/` | Permissions du rôle | Configuration des accès |

#### Permissions (`/api/permissions/permissions/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/permissions/permissions/` | Liste permissions | Catalogue des permissions |
| `GET` | `/api/permissions/permissions/by_app/` | Par application | Organisation par module |
| `GET` | `/api/permissions/permissions/active/` | Permissions actives | Filtrage par statut |

#### Rôles utilisateurs (`/api/permissions/user-roles/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/permissions/user-roles/` | Liste assignations | Gestion des rôles utilisateurs |
| `POST` | `/api/permissions/user-roles/` | Assigner rôle | Attribution de rôles |
| `POST` | `/api/permissions/user-roles/bulk_assign/` | Assignation en masse | Attribution multiple |
| `POST` | `/api/permissions/user-roles/{id}/extend/` | Prolonger rôle | Gestion des expirations |

#### Logs (`/api/permissions/logs/`)

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/permissions/logs/` | Liste logs | Audit des permissions |
| `GET` | `/api/permissions/logs/recent/` | Logs récents | Surveillance récente |

#### Endpoints spéciaux

| Méthode | Endpoint | Description | Utilité |
|---------|----------|-------------|---------|
| `GET` | `/api/permissions/user-permissions/{user_id}/` | Permissions utilisateur | Profil de permissions |
| `GET` | `/api/permissions/stats/` | Statistiques | Tableaux de bord |

### Rôles prédéfinis

| Rôle | Niveau | Couleur | Description |
|------|--------|---------|-------------|
| **Super Admin** | 0 | 🔴 Rouge | Accès total au système |
| **Manager** | 1 | 🟠 Orange | Gestion des équipes et rapports |
| **Sales** | 2 | 🟡 Jaune | Gestion des ventes et clients |
| **Stock Manager** | 2 | 🟢 Vert | Gestion des stocks |
| **Viewer** | 3 | 🔵 Bleu | Lecture seule |

### Fonctionnalités avancées
- **Hiérarchie des rôles** : 4 niveaux (0-3)
- **Permissions granulaires** : Par ressource et action
- **Expiration des rôles** : Gestion des rôles temporaires
- **Audit complet** : Logs de toutes les actions
- **Assignation en masse** : Gestion d'équipes
- **Conditions spéciales** : Permissions contextuelles

### Cas d'usage
- Contrôle d'accès granulaire
- Gestion des équipes
- Audit et conformité
- Sécurité des données
- Workflow d'approbation

---

## 🚀 Endpoints de test

Chaque module propose un endpoint de test pour vérifier le bon fonctionnement :

| Module | Endpoint | Description |
|--------|----------|-------------|
| Auth | `/api/auth/test/` | Test de l'API d'authentification |
| Customers | `/api/customers/test/` | Test de l'API clients |
| Inventory | `/api/inventory/test/` | Test de l'API inventaire |
| Stock | `/api/stock/test/` | Test de l'API stock |
| Sales | `/api/sales/test/` | Test de l'API ventes |
| Permissions | `/api/permissions/test/` | Test de l'API permissions |

---

## 📈 Statistiques générales

- **Total des modules** : 6
- **Total des endpoints** : ~80+
- **Méthodes HTTP supportées** : GET, POST, PUT, PATCH, DELETE
- **Authentification** : Token-based (DRF)
- **Format des données** : JSON
- **Pagination** : Supportée sur tous les endpoints de liste
- **Filtrage** : Avancé sur tous les modules
- **Recherche** : Textuelle sur la plupart des ressources

---

## 🔧 Intégration et utilisation

### 1. Authentification
```bash
# Connexion
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Utilisation du token
curl -X GET http://localhost:8000/api/customers/ \
  -H "Authorization: Token <votre_token>"
```

### 2. Workflow typique
1. **Connexion** → Récupération du token
2. **Gestion des clients** → Création/modification
3. **Gestion des produits** → Catalogue et variantes
4. **Gestion des stocks** → Mouvements et alertes
5. **Processus de vente** → Commandes, factures, paiements
6. **Gestion des permissions** → Rôles et accès

### 3. Collections Postman
Le projet inclut des collections Postman prêtes à l'emploi :
- `Postman_Inventory_Collection.json`
- `Postman_Permissions_Collection.json`
- `Postman_Sales_Collection.json`
- `Postman_Stock_Collection.json`

---

## 📚 Documentation détaillée

Pour chaque module, une documentation complète est disponible :
- `API_AUTH.md` - Authentification
- `API_CUSTOMERS.md` - Gestion clients
- `API_INVENTORY.md` - Gestion inventaire
- `API_STOCK.md` - Gestion stock
- `API_SALES.md` - Gestion ventes
- `API_PERMISSIONS.md` - Gestion permissions

---

## 🎯 Conclusion

Le système Baobab ERP offre une API REST complète et cohérente pour la gestion d'entreprise. Chaque module est conçu pour être autonome tout en s'intégrant parfaitement avec les autres composants du système. L'architecture modulaire permet une maintenance facile et une évolution progressive des fonctionnalités.

**Points forts :**
- ✅ Architecture REST cohérente
- ✅ Authentification sécurisée
- ✅ Permissions granulaires
- ✅ Documentation complète
- ✅ Tests intégrés
- ✅ Collections Postman
- ✅ Filtrage et recherche avancés
- ✅ Pagination et tri
- ✅ Audit et logs complets
