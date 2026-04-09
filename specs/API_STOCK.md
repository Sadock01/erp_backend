# API Stock - Documentation

## Vue d'ensemble

L'API Stock gère tous les mouvements de stock, ajustements, alertes et rapports pour le système CRM-ERP Baobab.

## Endpoints disponibles

### 1. Mouvements de Stock (`/api/stock/movements/`)

#### **GET** `/api/stock/movements/`
Lister tous les mouvements de stock

**Headers :**
```
Authorization: Token <votre_token>
```

**Paramètres de requête :**
- `product` : Filtrer par produit (ID)
- `variant` : Filtrer par variante (ID)
- `movement_type` : Filtrer par type de mouvement
- `is_approved` : Filtrer par statut d'approbation
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans nom produit, variante, référence, notes
- `ordering` : Tri (created_at, quantity, total_cost)

**Exemple de réponse :**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_name": "iPhone 15",
      "variant_name": "Rouge - 128GB",
      "movement_type": "purchase",
      "quantity": 50,
      "unit_cost": "600.00",
      "total_cost": "30000.00",
      "reference": "PO-2024-001",
      "user_name": "Admin User",
      "is_approved": true,
      "is_entry": true,
      "is_exit": false,
      "absolute_quantity": 50,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### **POST** `/api/stock/movements/`
Créer un nouveau mouvement de stock

**Headers :**
```
Authorization: Token <votre_token>
Content-Type: application/json
```

**Body :**
```json
{
  "product": 1,
  "variant": 1,
  "movement_type": "purchase",
  "quantity": 50,
  "unit_cost": "600.00",
  "reference": "PO-2024-001",
  "notes": "Commande d'achat iPhone 15"
}
```

#### **Actions spéciales :**

##### **GET** `/api/stock/movements/entries/`
Lister uniquement les entrées de stock

##### **GET** `/api/stock/movements/exits/`
Lister uniquement les sorties de stock

##### **GET** `/api/stock/movements/pending_approval/`
Lister les mouvements en attente d'approbation

##### **POST** `/api/stock/movements/{id}/approve/`
Approuver un mouvement de stock

##### **POST** `/api/stock/movements/{id}/reject/`
Rejeter un mouvement de stock

##### **GET** `/api/stock/movements/summary/`
Résumé des mouvements de stock

### 2. Ajustements de Stock (`/api/stock/adjustments/`)

#### **GET** `/api/stock/adjustments/`
Lister tous les ajustements de stock

**Paramètres de requête :**
- `product` : Filtrer par produit (ID)
- `variant` : Filtrer par variante (ID)
- `adjustment_type` : Filtrer par type d'ajustement
- `is_approved` : Filtrer par statut d'approbation
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans nom produit, variante, raison
- `ordering` : Tri (created_at, adjustment_quantity)

**Exemple de réponse :**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_name": "iPhone 15",
      "variant_name": "Rouge - 128GB",
      "adjustment_type": "inventory",
      "quantity_before": 45,
      "quantity_after": 50,
      "adjustment_quantity": 5,
      "reason": "Ajustement après inventaire",
      "user_name": "Admin User",
      "is_approved": true,
      "created_at": "2024-01-15T14:30:00Z"
    }
  ]
}
```

#### **POST** `/api/stock/adjustments/`
Créer un nouvel ajustement de stock

**Body :**
```json
{
  "product": 1,
  "variant": 1,
  "adjustment_type": "inventory",
  "quantity_before": 45,
  "quantity_after": 50,
  "reason": "Ajustement après inventaire"
}
```

#### **Actions spéciales :**

##### **GET** `/api/stock/adjustments/pending_approval/`
Lister les ajustements en attente d'approbation

##### **POST** `/api/stock/adjustments/{id}/approve/`
Approuver un ajustement de stock

##### **POST** `/api/stock/adjustments/{id}/reject/`
Rejeter un ajustement de stock

##### **GET** `/api/stock/adjustments/summary/`
Résumé des ajustements de stock

### 3. Alertes de Stock (`/api/stock/alerts/`)

#### **GET** `/api/stock/alerts/`
Lister toutes les alertes de stock

**Paramètres de requête :**
- `product` : Filtrer par produit (ID)
- `variant` : Filtrer par variante (ID)
- `alert_type` : Filtrer par type d'alerte
- `is_active` : Filtrer par statut actif
- `is_resolved` : Filtrer par statut résolu
- `search` : Recherche dans nom produit, variante
- `ordering` : Tri (created_at, current_quantity, threshold_quantity)

**Exemple de réponse :**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_name": "iPhone 15",
      "variant_name": "Rouge - 128GB",
      "alert_type": "low_stock",
      "current_quantity": 5,
      "threshold_quantity": 10,
      "is_active": true,
      "is_resolved": false,
      "is_low_stock": true,
      "is_out_of_stock": false,
      "is_overstock": false,
      "created_at": "2024-01-15T16:30:00Z"
    }
  ]
}
```

#### **Actions spéciales :**

##### **GET** `/api/stock/alerts/active/`
Lister uniquement les alertes actives

##### **GET** `/api/stock/alerts/resolved/`
Lister uniquement les alertes résolues

##### **POST** `/api/stock/alerts/{id}/resolve/`
Résoudre une alerte de stock

##### **GET** `/api/stock/alerts/summary/`
Résumé des alertes de stock

### 4. Rapports de Stock (`/api/stock/reports/`)

#### **GET** `/api/stock/reports/`
Lister tous les rapports de stock

**Paramètres de requête :**
- `report_type` : Filtrer par type de rapport
- `is_generated` : Filtrer par statut de génération
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans titre, description
- `ordering` : Tri (created_at, generated_at)

**Exemple de réponse :**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "report_type": "inventory",
      "title": "Rapport d'inventaire mensuel",
      "description": "Rapport d'inventaire pour janvier 2024",
      "date_from": "2024-01-01",
      "date_to": "2024-01-31",
      "user_name": "Admin User",
      "is_generated": true,
      "generated_at": "2024-01-31T18:00:00Z",
      "period_days": 31,
      "created_at": "2024-01-31T17:30:00Z"
    }
  ]
}
```

#### **POST** `/api/stock/reports/`
Créer un nouveau rapport de stock

**Body :**
```json
{
  "report_type": "inventory",
  "title": "Rapport d'inventaire mensuel",
  "description": "Rapport d'inventaire pour janvier 2024",
  "date_from": "2024-01-01",
  "date_to": "2024-01-31",
  "filters": {
    "category": 1,
    "status": "active"
  }
}
```

#### **Actions spéciales :**

##### **POST** `/api/stock/reports/{id}/generate/`
Générer un rapport de stock

##### **GET** `/api/stock/reports/summary/`
Résumé des rapports de stock

## Types de données

### Types de mouvements de stock
- `purchase` : Achat
- `sale` : Vente
- `return` : Retour
- `transfer` : Transfert
- `adjustment` : Ajustement
- `damage` : Dégâts
- `theft` : Vol
- `expired` : Périmé

### Types d'ajustements
- `inventory` : Inventaire
- `damage` : Dégâts
- `theft` : Vol
- `expired` : Périmé
- `other` : Autre

### Types d'alertes
- `low_stock` : Stock bas
- `out_of_stock` : Rupture de stock
- `overstock` : Surstock

### Types de rapports
- `inventory` : Inventaire
- `movements` : Mouvements
- `adjustments` : Ajustements
- `alerts` : Alertes
- `summary` : Résumé

## Exemples d'utilisation

### 1. Créer un mouvement d'achat
```bash
curl -X POST http://localhost:8000/api/stock/movements/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "variant": 1,
    "movement_type": "purchase",
    "quantity": 50,
    "unit_cost": "600.00",
    "reference": "PO-2024-001",
    "notes": "Commande d'achat iPhone 15"
  }'
```

### 2. Créer un ajustement de stock
```bash
curl -X POST http://localhost:8000/api/stock/adjustments/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product": 1,
    "variant": 1,
    "adjustment_type": "inventory",
    "quantity_before": 45,
    "quantity_after": 50,
    "reason": "Ajustement après inventaire"
  }'
```

### 3. Lister les alertes actives
```bash
curl -X GET http://localhost:8000/api/stock/alerts/active/ \
  -H "Authorization: Token <votre_token>"
```

### 4. Générer un rapport
```bash
curl -X POST http://localhost:8000/api/stock/reports/1/generate/ \
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
2. **Validation des données** : Les quantités ne peuvent pas être nulles
3. **Cohérence des données** : Les variantes doivent appartenir au produit sélectionné
4. **Approbation** : Les mouvements et ajustements peuvent nécessiter une approbation
5. **Filtrage par date** : Utilisez le format YYYY-MM-DD pour les filtres de date
