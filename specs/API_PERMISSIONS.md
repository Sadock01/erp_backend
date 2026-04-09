# API Permissions - Documentation

## Vue d'ensemble

L'API Permissions gère le système de rôles et permissions pour le CRM-ERP Baobab. Elle permet de contrôler finement l'accès aux différentes fonctionnalités du système.

## Modèles principaux

### 1. Role (Rôle)
- **Nom** : Nom unique du rôle (ex: Admin, Manager, Sales)
- **Description** : Description détaillée du rôle
- **Niveau** : Niveau hiérarchique (0=Admin, 1=Manager, 2=User, 3=Viewer)
- **Couleur** : Couleur hexadécimale pour l'affichage
- **Icône** : Classe CSS de l'icône
- **Système** : Indique si c'est un rôle système (non supprimable)

### 2. Permission (Permission)
- **Nom** : Nom lisible de la permission
- **Code** : Code unique de la permission (ex: customers_view)
- **Application** : Nom de l'application (customers, sales, inventory, stock)
- **Ressource** : Ressource concernée (customer, order, product, stock)
- **Action** : Type d'action (view, create, update, delete, manage)

### 3. UserRole (Rôle d'utilisateur)
- **Utilisateur** : Utilisateur concerné
- **Rôle** : Rôle assigné
- **Assigné par** : Utilisateur qui a assigné le rôle
- **Expiration** : Date d'expiration du rôle (optionnel)
- **Actif** : Indique si l'assignation est active

### 4. PermissionLog (Log de permission)
- **Action** : Type d'action effectuée
- **Utilisateur** : Utilisateur concerné
- **Cible** : Utilisateur cible de l'action
- **Détails** : Détails supplémentaires de l'action

## Endpoints disponibles

### 1. Test (`/api/permissions/test/`)

#### **GET** `/api/permissions/test/`
Test simple de l'API Permissions

**Exemple de réponse :**
```json
{
  "message": "API Permissions fonctionne correctement !",
  "endpoints": [
    "GET /api/permissions/roles/ - Lister les rôles",
    "POST /api/permissions/roles/ - Créer un rôle",
    "GET /api/permissions/permissions/ - Lister les permissions",
    "GET /api/permissions/user-roles/ - Lister les rôles d'utilisateurs",
    "POST /api/permissions/user-roles/ - Assigner un rôle",
    "GET /api/permissions/logs/ - Lister les logs de permissions",
    "GET /api/permissions/stats/ - Statistiques des permissions"
  ]
}
```

### 2. Rôles (`/api/permissions/roles/`)

#### **GET** `/api/permissions/roles/`
Lister tous les rôles

**Headers :**
```
Authorization: Token <votre_token>
```

**Paramètres de requête :**
- `is_active` : Filtrer par statut actif
- `is_system` : Filtrer par rôles système
- `level` : Filtrer par niveau hiérarchique
- `search` : Recherche dans nom et description
- `ordering` : Tri (name, level, created_at)

**Exemple de réponse :**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Super Admin",
      "description": "Accès total au système",
      "level": 0,
      "color": "#dc3545",
      "icon": "fas fa-user-shield",
      "user_count": 1,
      "is_active": true,
      "is_system": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### **POST** `/api/permissions/roles/`
Créer un nouveau rôle

**Headers :**
```
Authorization: Token <votre_token>
Content-Type: application/json
```

**Body :**
```json
{
  "name": "Sales Manager",
  "description": "Gestionnaire des ventes",
  "level": 1,
  "color": "#28a745",
  "icon": "fas fa-chart-line",
  "is_active": true
}
```

#### **Actions spéciales :**

##### **GET** `/api/permissions/roles/active/`
Lister uniquement les rôles actifs

##### **GET** `/api/permissions/roles/system/`
Lister uniquement les rôles système

##### **GET** `/api/permissions/roles/{id}/permissions/`
Lister les permissions d'un rôle

**Exemple de réponse :**
```json
{
  "role": {
    "id": 1,
    "name": "Sales Manager",
    "description": "Gestionnaire des ventes"
  },
  "permissions": [...],
  "granted_permissions": [...],
  "denied_permissions": [...],
  "total_permissions": 25
}
```

##### **POST** `/api/permissions/roles/{id}/assign_permission/`
Assigner une permission à un rôle

**Body :**
```json
{
  "permission_id": 1,
  "granted": true,
  "conditions": {},
  "notes": "Permission accordée pour la gestion des ventes"
}
```

### 3. Permissions (`/api/permissions/permissions/`)

#### **GET** `/api/permissions/permissions/`
Lister toutes les permissions

**Paramètres de requête :**
- `is_active` : Filtrer par statut actif
- `is_system` : Filtrer par permissions système
- `app_label` : Filtrer par application
- `action` : Filtrer par action
- `resource` : Filtrer par ressource
- `search` : Recherche dans nom, code et description
- `ordering` : Tri (name, app_label, action, resource)

**Exemple de réponse :**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Voir les clients",
      "codename": "customers_view",
      "app_label": "customers",
      "resource": "customer",
      "action": "view",
      "full_codename": "customers.customer.view",
      "is_active": true,
      "is_system": false
    }
  ]
}
```

#### **Actions spéciales :**

##### **GET** `/api/permissions/permissions/by_app/`
Lister les permissions par application

**Paramètres :**
- `app` : Nom de l'application (customers, sales, inventory, stock)

**Exemple de réponse :**
```json
{
  "customers": [
    {
      "id": 1,
      "name": "Voir les clients",
      "codename": "customers_view",
      "app_label": "customers",
      "resource": "customer",
      "action": "view"
    }
  ],
  "sales": [
    {
      "id": 2,
      "name": "Créer des commandes",
      "codename": "sales_orders_create",
      "app_label": "sales",
      "resource": "order",
      "action": "create"
    }
  ]
}
```

##### **GET** `/api/permissions/permissions/active/`
Lister uniquement les permissions actives

### 4. Rôles d'utilisateurs (`/api/permissions/user-roles/`)

#### **GET** `/api/permissions/user-roles/`
Lister tous les rôles d'utilisateurs

**Paramètres de requête :**
- `is_active` : Filtrer par statut actif
- `role` : Filtrer par rôle (ID)
- `user` : Filtrer par utilisateur (ID)
- `assigned_by` : Filtrer par utilisateur qui a assigné
- `search` : Recherche dans nom utilisateur, email, nom rôle
- `ordering` : Tri (assigned_at, expires_at, created_at)

**Exemple de réponse :**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user": 1,
      "role": 2,
      "assigned_by": 1,
      "assigned_at": "2024-01-15T10:30:00Z",
      "expires_at": null,
      "is_active": true,
      "user_name": "admin",
      "user_email": "admin@example.com",
      "role_name": "Sales Manager",
      "role_color": "#28a745",
      "assigned_by_name": "admin",
      "is_expired": false,
      "days_until_expiry": null,
      "notes": "Rôle assigné pour la gestion des ventes"
    }
  ]
}
```

#### **POST** `/api/permissions/user-roles/`
Assigner un rôle à un utilisateur

**Body :**
```json
{
  "user": 1,
  "role": 2,
  "expires_at": "2024-12-31T23:59:59Z",
  "notes": "Rôle temporaire pour un projet"
}
```

#### **Actions spéciales :**

##### **GET** `/api/permissions/user-roles/active/`
Lister uniquement les rôles actifs

##### **GET** `/api/permissions/user-roles/expired/`
Lister les rôles expirés

##### **POST** `/api/permissions/user-roles/bulk_assign/`
Assigner un rôle à plusieurs utilisateurs

**Body :**
```json
{
  "user_ids": [1, 2, 3],
  "role_id": 2,
  "expires_at": "2024-12-31T23:59:59Z",
  "notes": "Assignation en masse pour un projet"
}
```

##### **POST** `/api/permissions/user-roles/{id}/extend/`
Prolonger un rôle

**Body :**
```json
{
  "expires_at": "2024-12-31T23:59:59Z"
}
```

##### **POST** `/api/permissions/user-roles/{id}/deactivate/`
Désactiver un rôle

### 5. Logs de permissions (`/api/permissions/logs/`)

#### **GET** `/api/permissions/logs/`
Lister tous les logs de permissions

**Paramètres de requête :**
- `action` : Filtrer par action
- `user` : Filtrer par utilisateur
- `target_user` : Filtrer par utilisateur cible
- `role` : Filtrer par rôle
- `permission` : Filtrer par permission
- `search` : Recherche dans noms d'utilisateurs et rôles
- `ordering` : Tri (created_at, action)

**Exemple de réponse :**
```json
{
  "count": 100,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "action": "role_assigned",
      "user": 1,
      "target_user": 2,
      "role": 2,
      "permission": null,
      "details": {
        "role_name": "Sales Manager",
        "user_name": "john_doe"
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "user_name": "admin",
      "target_user_name": "john_doe",
      "role_name": "Sales Manager",
      "permission_name": null,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### **Actions spéciales :**

##### **GET** `/api/permissions/logs/by_user/`
Lister les logs par utilisateur

**Paramètres :**
- `user_id` : ID de l'utilisateur

##### **GET** `/api/permissions/logs/by_action/`
Lister les logs par action

**Paramètres :**
- `action` : Type d'action (role_assigned, role_removed, etc.)

##### **GET** `/api/permissions/logs/recent/`
Lister les logs récents

**Paramètres :**
- `days` : Nombre de jours (défaut: 7)

### 6. Endpoints spéciaux

#### **GET** `/api/permissions/user-permissions/{user_id}/`
Récupérer les permissions d'un utilisateur

**Exemple de réponse :**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true
  },
  "roles": [
    {
      "id": 2,
      "name": "Sales Manager",
      "description": "Gestionnaire des ventes",
      "level": 1,
      "color": "#28a745",
      "icon": "fas fa-chart-line",
      "user_count": 3,
      "is_active": true
    }
  ],
  "permissions": [
    {
      "id": 1,
      "name": "Voir les clients",
      "codename": "customers_view",
      "app_label": "customers",
      "resource": "customer",
      "action": "view"
    }
  ],
  "total_permissions": 25,
  "total_roles": 1
}
```

#### **GET** `/api/permissions/stats/`
Récupérer les statistiques des permissions

**Exemple de réponse :**
```json
{
  "total_users": 10,
  "total_roles": 5,
  "total_permissions": 50,
  "active_roles": 4,
  "system_roles": 2,
  "users_by_role": {
    "Super Admin": 1,
    "Sales Manager": 3,
    "Sales": 5,
    "Viewer": 1
  },
  "permissions_by_app": {
    "customers": 10,
    "sales": 15,
    "inventory": 12,
    "stock": 8,
    "permissions": 5
  },
  "recent_assignments": [...],
  "recent_logs": [...]
}
```

## Rôles prédéfinis

### 🔴 Super Admin (Level 0)
- Accès total à tout le système
- Gestion des utilisateurs et rôles
- Configuration système
- Couleur : #dc3545 (rouge)

### 🟠 Manager (Level 1)
- Gestion des ventes et clients
- Rapports et analyses
- Gestion des stocks
- Gestion des équipes
- Couleur : #fd7e14 (orange)

### 🟡 Sales (Level 2)
- Création et gestion des commandes
- Gestion des clients
- Création des devis
- Suivi des factures
- Couleur : #ffc107 (jaune)

### 🟢 Stock Manager (Level 2)
- Gestion des stocks
- Mouvements de stock
- Alertes et ajustements
- Rapports de stock
- Couleur : #28a745 (vert)

### 🔵 Viewer (Level 3)
- Lecture seule
- Rapports limités
- Pas de modifications
- Couleur : #007bff (bleu)

## Permissions par module

### Customers
- `customers.customer.view` - Voir les clients
- `customers.customer.create` - Créer des clients
- `customers.customer.update` - Modifier les clients
- `customers.customer.delete` - Supprimer les clients
- `customers.customer.manage` - Gestion complète des clients

### Sales
- `sales.order.view` - Voir les commandes
- `sales.order.create` - Créer des commandes
- `sales.order.update` - Modifier les commandes
- `sales.order.cancel` - Annuler des commandes
- `sales.invoice.manage` - Gestion complète des factures
- `sales.proforma.manage` - Gestion complète des devis
- `sales.payment.manage` - Gestion complète des paiements

### Inventory
- `inventory.product.view` - Voir les produits
- `inventory.product.create` - Créer des produits
- `inventory.product.update` - Modifier les produits
- `inventory.product.delete` - Supprimer les produits
- `inventory.category.manage` - Gestion des catégories

### Stock
- `stock.movement.view` - Voir les mouvements
- `stock.movement.create` - Créer des mouvements
- `stock.alert.manage` - Gérer les alertes
- `stock.adjustment.manage` - Gérer les ajustements

## Exemples d'utilisation

### 1. Créer un rôle personnalisé
```bash
curl -X POST http://localhost:8000/api/permissions/roles/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Manager",
    "description": "Gestionnaire de projet",
    "level": 1,
    "color": "#6f42c1",
    "icon": "fas fa-project-diagram",
    "is_active": true
  }'
```

### 2. Assigner un rôle à un utilisateur
```bash
curl -X POST http://localhost:8000/api/permissions/user-roles/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 1,
    "role": 2,
    "expires_at": "2024-12-31T23:59:59Z",
    "notes": "Rôle temporaire pour un projet"
  }'
```

### 3. Assigner une permission à un rôle
```bash
curl -X POST http://localhost:8000/api/permissions/roles/2/assign_permission/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_id": 1,
    "granted": true,
    "conditions": {},
    "notes": "Permission accordée pour la gestion des ventes"
  }'
```

### 4. Récupérer les permissions d'un utilisateur
```bash
curl -X GET http://localhost:8000/api/permissions/user-permissions/1/ \
  -H "Authorization: Token <votre_token>"
```

### 5. Lister les rôles actifs
```bash
curl -X GET http://localhost:8000/api/permissions/roles/active/ \
  -H "Authorization: Token <votre_token>"
```

### 6. Assigner un rôle à plusieurs utilisateurs
```bash
curl -X POST http://localhost:8000/api/permissions/user-roles/bulk_assign/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "user_ids": [1, 2, 3],
    "role_id": 2,
    "expires_at": "2024-12-31T23:59:59Z",
    "notes": "Assignation en masse pour un projet"
  }'
```

### 7. Consulter les statistiques
```bash
curl -X GET http://localhost:8000/api/permissions/stats/ \
  -H "Authorization: Token <votre_token>"
```

### 8. Lister les logs récents
```bash
curl -X GET http://localhost:8000/api/permissions/logs/recent/?days=30 \
  -H "Authorization: Token <votre_token>"
```

## Codes de statut HTTP

- `200` : Succès
- `201` : Créé avec succès
- `400` : Erreur de validation
- `401` : Non authentifié
- `403` : Non autorisé
- `404` : Non trouvé
- `500` : Erreur serveur

## Notes importantes

1. **Authentification requise** : Tous les endpoints nécessitent un token d'authentification
2. **Rôles système** : Les rôles système ne peuvent pas être supprimés
3. **Permissions granulaires** : Contrôle précis des accès par ressource et action
4. **Expiration des rôles** : Les rôles peuvent avoir une date d'expiration
5. **Audit complet** : Toutes les actions sont loggées
6. **Hiérarchie des rôles** : Les niveaux permettent une gestion hiérarchique
7. **Conditions spéciales** : Les permissions peuvent avoir des conditions particulières
8. **Interface d'administration** : Gestion via Django Admin avec interface personnalisée
