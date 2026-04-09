# API Sales - Documentation

## Vue d'ensemble

L'API Sales gère toutes les ventes, commandes, factures, devis et paiements pour le système CRM-ERP Baobab.

## Endpoints disponibles

### 1. Commandes (`/api/sales/orders/`)

#### **GET** `/api/sales/orders/`
Lister toutes les commandes

**Headers :**
```
Authorization: Token <votre_token>
```

**Paramètres de requête :**
- `customer` : Filtrer par client (ID)
- `status` : Filtrer par statut
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans numéro commande, nom client, notes
- `ordering` : Tri (created_at, order_date, total_amount)

**Exemple de réponse :**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "customer_name": "Jean Dupont",
      "order_number": "CMD20240115-0001",
      "status": "pending",
      "order_date": "2024-01-15T10:30:00Z",
      "total_amount": "1199.99",
      "user_name": "Admin User",
      "items_count": 2,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### **POST** `/api/sales/orders/`
Créer une nouvelle commande

**Headers :**
```
Authorization: Token <votre_token>
Content-Type: application/json
```

**Body :**
```json
{
  "customer": 1,
  "status": "pending",
  "order_date": "2024-01-15T10:30:00Z",
  "delivery_date": "2024-01-20T10:30:00Z",
  "tax_rate": "20.00",
  "discount_rate": "5.00",
  "notes": "Commande urgente",
  "internal_notes": "Client VIP",
  "items": [
    {
      "product": 1,
      "variant": 1,
      "quantity": 2,
      "unit_price": "999.99",
      "discount_rate": "0.00"
    }
  ]
}
```

#### **Actions spéciales :**

##### **GET** `/api/sales/orders/pending/`
Lister uniquement les commandes en attente

##### **GET** `/api/sales/orders/confirmed/`
Lister uniquement les commandes confirmées

##### **GET** `/api/sales/orders/shipped/`
Lister uniquement les commandes expédiées

##### **GET** `/api/sales/orders/delivered/`
Lister uniquement les commandes livrées

##### **GET** `/api/sales/orders/cancelled/`
Lister uniquement les commandes annulées

##### **POST** `/api/sales/orders/{id}/confirm/`
Confirmer une commande

##### **POST** `/api/sales/orders/{id}/ship/`
Marquer une commande comme expédiée

##### **POST** `/api/sales/orders/{id}/deliver/`
Marquer une commande comme livrée

##### **POST** `/api/sales/orders/{id}/cancel/`
Annuler une commande

##### **GET** `/api/sales/orders/summary/`
Résumé des commandes

### 2. Articles de Commande (`/api/sales/order-items/`)

#### **GET** `/api/sales/order-items/`
Lister tous les articles de commande

**Paramètres de requête :**
- `order` : Filtrer par commande (ID)
- `product` : Filtrer par produit (ID)
- `variant` : Filtrer par variante (ID)
- `search` : Recherche dans nom produit, variante
- `ordering` : Tri (created_at, quantity, unit_price, total_price)

**Exemple de réponse :**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "order_number": "CMD20240115-0001",
      "product_name": "iPhone 15 - Rouge - 128GB",
      "quantity": 2,
      "unit_price": "999.99",
      "total_price": "1999.98",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### **POST** `/api/sales/order-items/`
Créer un nouvel article de commande

**Body :**
```json
{
  "order": 1,
  "product": 1,
  "variant": 1,
  "quantity": 2,
  "unit_price": "999.99",
  "discount_rate": "5.00"
}
```

### 3. Factures (`/api/sales/invoices/`)

#### **GET** `/api/sales/invoices/`
Lister toutes les factures

**Paramètres de requête :**
- `status` : Filtrer par statut
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans numéro facture, nom client
- `ordering` : Tri (created_at, invoice_date, due_date, total_amount)

**Exemple de réponse :**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "invoice_number": "FAC20240115-0001",
      "customer_name": "Jean Dupont",
      "order_number": "CMD20240115-0001",
      "status": "sent",
      "invoice_date": "2024-01-15T11:00:00Z",
      "due_date": "2024-02-15T11:00:00Z",
      "total_amount": "1199.99",
      "paid_amount": "0.00",
      "remaining_amount": "1199.99",
      "is_overdue": false,
      "payment_percentage": 0.0,
      "created_at": "2024-01-15T11:00:00Z"
    }
  ]
}
```

#### **POST** `/api/sales/invoices/`
Créer une nouvelle facture

**Body :**
```json
{
  "order": 1,
  "status": "draft",
  "invoice_date": "2024-01-15T11:00:00Z",
  "due_date": "2024-02-15T11:00:00Z",
  "notes": "Facture pour commande urgente"
}
```

#### **Actions spéciales :**

##### **GET** `/api/sales/invoices/draft/`
Lister uniquement les factures en brouillon

##### **GET** `/api/sales/invoices/sent/`
Lister uniquement les factures envoyées

##### **GET** `/api/sales/invoices/paid/`
Lister uniquement les factures payées

##### **GET** `/api/sales/invoices/overdue/`
Lister uniquement les factures en retard

##### **POST** `/api/sales/invoices/{id}/send/`
Envoyer une facture

##### **POST** `/api/sales/invoices/{id}/mark_paid/`
Marquer une facture comme payée

##### **GET** `/api/sales/invoices/summary/`
Résumé des factures

### 4. Devis (`/api/sales/proformas/`)

#### **GET** `/api/sales/proformas/`
Lister tous les devis

**Paramètres de requête :**
- `customer` : Filtrer par client (ID)
- `status` : Filtrer par statut
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans numéro devis, nom client
- `ordering` : Tri (created_at, proforma_date, valid_until, total_amount)

**Exemple de réponse :**
```json
{
  "count": 6,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "proforma_number": "DEV20240115-0001",
      "customer_name": "Jean Dupont",
      "status": "sent",
      "proforma_date": "2024-01-15T09:00:00Z",
      "valid_until": "2024-01-30T09:00:00Z",
      "total_amount": "1199.99",
      "is_expired": false,
      "created_at": "2024-01-15T09:00:00Z"
    }
  ]
}
```

#### **POST** `/api/sales/proformas/`
Créer un nouveau devis

**Body :**
```json
{
  "customer": 1,
  "status": "draft",
  "proforma_date": "2024-01-15T09:00:00Z",
  "valid_until": "2024-01-30T09:00:00Z",
  "subtotal": "999.99",
  "tax_rate": "20.00",
  "tax_amount": "199.99",
  "total_amount": "1199.99",
  "notes": "Devis pour iPhone 15"
}
```

#### **Actions spéciales :**

##### **GET** `/api/sales/proformas/draft/`
Lister uniquement les devis en brouillon

##### **GET** `/api/sales/proformas/sent/`
Lister uniquement les devis envoyés

##### **GET** `/api/sales/proformas/accepted/`
Lister uniquement les devis acceptés

##### **GET** `/api/sales/proformas/expired/`
Lister uniquement les devis expirés

##### **POST** `/api/sales/proformas/{id}/send/`
Envoyer un devis

##### **POST** `/api/sales/proformas/{id}/accept/`
Accepter un devis

##### **POST** `/api/sales/proformas/{id}/reject/`
Rejeter un devis

##### **GET** `/api/sales/proformas/summary/`
Résumé des devis

### 5. Paiements (`/api/sales/payments/`)

#### **GET** `/api/sales/payments/`
Lister tous les paiements

**Paramètres de requête :**
- `invoice` : Filtrer par facture (ID)
- `payment_method` : Filtrer par méthode de paiement
- `user` : Filtrer par utilisateur
- `date_from` : Date de début (YYYY-MM-DD)
- `date_to` : Date de fin (YYYY-MM-DD)
- `search` : Recherche dans numéro facture, référence, notes
- `ordering` : Tri (created_at, payment_date, amount)

**Exemple de réponse :**
```json
{
  "count": 12,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "invoice_number": "FAC20240115-0001",
      "customer_name": "Jean Dupont",
      "payment_method": "bank_transfer",
      "amount": "1199.99",
      "payment_date": "2024-01-16T14:30:00Z",
      "reference": "VIR-2024-001",
      "created_at": "2024-01-16T14:30:00Z"
    }
  ]
}
```

#### **POST** `/api/sales/payments/`
Créer un nouveau paiement

**Body :**
```json
{
  "invoice": 1,
  "payment_method": "bank_transfer",
  "amount": "1199.99",
  "payment_date": "2024-01-16T14:30:00Z",
  "reference": "VIR-2024-001",
  "notes": "Paiement par virement bancaire"
}
```

#### **Actions spéciales :**

##### **GET** `/api/sales/payments/by_method/?method=cash`
Lister les paiements par méthode

##### **GET** `/api/sales/payments/summary/`
Résumé des paiements

## Types de données

### Statuts des commandes
- `pending` : En attente
- `confirmed` : Confirmée
- `shipped` : Expédiée
- `delivered` : Livrée
- `cancelled` : Annulée

### Statuts des factures
- `draft` : Brouillon
- `sent` : Envoyée
- `paid` : Payée
- `partial` : Partiellement payée
- `overdue` : En retard

### Statuts des devis
- `draft` : Brouillon
- `sent` : Envoyé
- `accepted` : Accepté
- `rejected` : Rejeté
- `expired` : Expiré

### Méthodes de paiement
- `cash` : Espèces
- `check` : Chèque
- `bank_transfer` : Virement bancaire
- `credit_card` : Carte de crédit
- `paypal` : PayPal
- `other` : Autre

## Exemples d'utilisation

### 1. Créer une commande complète
```bash
curl -X POST http://localhost:8000/api/sales/orders/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": 1,
    "status": "pending",
    "order_date": "2024-01-15T10:30:00Z",
    "delivery_date": "2024-01-20T10:30:00Z",
    "tax_rate": "20.00",
    "discount_rate": "5.00",
    "notes": "Commande urgente",
    "items": [
      {
        "product": 1,
        "variant": 1,
        "quantity": 2,
        "unit_price": "999.99",
        "discount_rate": "0.00"
      }
    ]
  }'
```

### 2. Créer une facture
```bash
curl -X POST http://localhost:8000/api/sales/invoices/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "order": 1,
    "status": "draft",
    "invoice_date": "2024-01-15T11:00:00Z",
    "due_date": "2024-02-15T11:00:00Z",
    "notes": "Facture pour commande urgente"
  }'
```

### 3. Créer un devis
```bash
curl -X POST http://localhost:8000/api/sales/proformas/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer": 1,
    "status": "draft",
    "proforma_date": "2024-01-15T09:00:00Z",
    "valid_until": "2024-01-30T09:00:00Z",
    "subtotal": "999.99",
    "tax_rate": "20.00",
    "tax_amount": "199.99",
    "total_amount": "1199.99",
    "notes": "Devis pour iPhone 15"
  }'
```

### 4. Enregistrer un paiement
```bash
curl -X POST http://localhost:8000/api/sales/payments/ \
  -H "Authorization: Token <votre_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice": 1,
    "payment_method": "bank_transfer",
    "amount": "1199.99",
    "payment_date": "2024-01-16T14:30:00Z",
    "reference": "VIR-2024-001",
    "notes": "Paiement par virement bancaire"
  }'
```

### 5. Confirmer une commande
```bash
curl -X POST http://localhost:8000/api/sales/orders/1/confirm/ \
  -H "Authorization: Token <votre_token>"
```

### 6. Envoyer une facture
```bash
curl -X POST http://localhost:8000/api/sales/invoices/1/send/ \
  -H "Authorization: Token <votre_token>"
```

### 7. Lister les factures en retard
```bash
curl -X GET http://localhost:8000/api/sales/invoices/overdue/ \
  -H "Authorization: Token <votre_token>"
```

### 8. Résumé des commandes
```bash
curl -X GET http://localhost:8000/api/sales/orders/summary/ \
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
2. **Validation des données** : Les quantités et montants doivent être positifs
3. **Cohérence des données** : Les variantes doivent appartenir au produit sélectionné
4. **Calculs automatiques** : Les totaux sont calculés automatiquement
5. **Numérotation automatique** : Les numéros de commande, facture et devis sont générés automatiquement
6. **Filtrage par date** : Utilisez le format YYYY-MM-DD pour les filtres de date
7. **Gestion des statuts** : Les statuts sont mis à jour via les actions spéciales
8. **Suivi des paiements** : Les montants payés sont calculés automatiquement
