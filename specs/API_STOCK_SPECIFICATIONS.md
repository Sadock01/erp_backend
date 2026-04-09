# 📦 API Specifications - Stock Management
## Baobab ERP System

This document provides comprehensive specifications for all stock management APIs in the Baobab ERP system.

---

## 🌐 Base URL
```
http://localhost:8000/api/stock/
```
**Production:** `https://your-domain.com/api/stock/`

---

## 🔐 Authentication
All API endpoints require authentication using Token authentication:

```http
Authorization: Token <your_token_here>
```

**How to get a token:**
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "your_email@example.com",
    "password": "your_password"
}
```

---

## 📋 Table of Contents
1. [Stock Movements Management](#stock-movements-management)
2. [Stock Adjustments Management](#stock-adjustments-management)
3. [Stock Alerts Management](#stock-alerts-management)
4. [Stock Reports Management](#stock-reports-management)
5. [Stock Analytics](#stock-analytics)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)

---

## 📦 Stock Movements Management

### 1. List Stock Movements
**Endpoint:** `GET /api/stock/movements/`

**Description:** Retrieve all stock movements with optional filtering and pagination.

**Required Permission:** `stock_movements_view`

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `product` (int): Filter by product ID
- `variant` (int): Filter by variant ID
- `movement_type` (string): Filter by movement type (in, out, adjustment, transfer, return)
- `is_approved` (boolean): Filter by approval status
- `user` (int): Filter by user ID
- `date_from` (date): Filter movements from date (YYYY-MM-DD)
- `date_to` (date): Filter movements to date (YYYY-MM-DD)
- `search` (string): Search in product name, variant name, reference, notes
- `ordering` (string): Order by field (created_at, quantity, total_cost)

**Response (200 OK):**
```json
{
    "count": 250,
    "next": "http://localhost:8000/api/stock/movements/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "product_name": "iPhone 15",
            "variant_name": "128GB Noir",
            "movement_type": "in",
            "quantity": 50,
            "unit_cost": "800.00",
            "total_cost": "40000.00",
            "reference": "PO-2024-001",
            "user_name": "Admin User",
            "is_approved": true,
            "is_entry": true,
            "is_exit": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Stock Movement Details
**Endpoint:** `GET /api/stock/movements/{id}/`

**Required Permission:** `stock_movements_view`

**Response (200 OK):**
```json
{
    "id": 1,
    "product": 1,
    "product_name": "iPhone 15",
    "variant": 1,
    "variant_name": "128GB Noir",
    "movement_type": "in",
    "quantity": 50,
    "unit_cost": "800.00",
    "total_cost": "40000.00",
    "reference": "PO-2024-001",
    "notes": "Réception de la commande fournisseur",
    "user": 1,
    "user_name": "Admin User",
    "is_approved": true,
    "approved_by": 1,
    "approved_by_name": "Admin User",
    "approved_at": "2024-01-15T10:35:00Z",
    "is_entry": true,
    "is_exit": false,
    "absolute_quantity": 50,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
}
```

### 3. Create Stock Movement
**Endpoint:** `POST /api/stock/movements/`

**Required Permission:** `stock_movements_create`

**Request Body:**
```json
{
    "product": 1,
    "variant": 1,
    "movement_type": "in",
    "quantity": 50,
    "unit_cost": "800.00",
    "reference": "PO-2024-001",
    "notes": "Réception de la commande fournisseur"
}
```

**Response (201 Created):** Same as Get Stock Movement Details

### 4. Update Stock Movement
**Endpoint:** `PUT /api/stock/movements/{id}/` or `PATCH /api/stock/movements/{id}/`

**Required Permission:** `stock_movements_create`

**Request Body (PATCH - Partial Update):**
```json
{
    "quantity": 45,
    "unit_cost": "820.00",
    "notes": "Quantité ajustée après vérification"
}
```

**Response (200 OK):** Same as Get Stock Movement Details

### 5. Delete Stock Movement
**Endpoint:** `DELETE /api/stock/movements/{id}/`

**Required Permission:** `stock_movements_create`

**Response (204 No Content):** Empty response body

### 6. Stock Movement Filtering

#### Entries Only
**Endpoint:** `GET /api/stock/movements/entries/`

**Required Permission:** `stock_movements_view`

**Description:** List only stock entries (positive quantities)

**Response (200 OK):** List of stock entries

#### Exits Only
**Endpoint:** `GET /api/stock/movements/exits/`

**Required Permission:** `stock_movements_view`

**Description:** List only stock exits (negative quantities)

**Response (200 OK):** List of stock exits

#### Pending Approval
**Endpoint:** `GET /api/stock/movements/pending_approval/`

**Required Permission:** `stock_movements_view`

**Description:** List movements pending approval

**Response (200 OK):** List of pending movements

### 7. Stock Movement Approval

#### Approve Movement
**Endpoint:** `POST /api/stock/movements/{id}/approve/`

**Required Permission:** `stock_movements_create`

**Response (200 OK):** Updated movement details

#### Reject Movement
**Endpoint:** `POST /api/stock/movements/{id}/reject/`

**Required Permission:** `stock_movements_create`

**Response (200 OK):** Updated movement details

### 8. Stock Movements Summary
**Endpoint:** `GET /api/stock/movements/summary/`

**Required Permission:** `stock_movements_view`

**Description:** Get comprehensive movement statistics.

**Response (200 OK):**
```json
{
    "total_movements": 250,
    "total_entries": 120,
    "total_exits": 130,
    "total_quantity_entries": 5000,
    "total_quantity_exits": -4500,
    "total_cost_entries": 400000.00,
    "total_cost_exits": 350000.00
}
```

---

## 🔧 Stock Adjustments Management

### 1. List Stock Adjustments
**Endpoint:** `GET /api/stock/adjustments/`

**Description:** Retrieve all stock adjustments with optional filtering and pagination.

**Required Permission:** `stock_adjustments_manage`

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `product` (int): Filter by product ID
- `variant` (int): Filter by variant ID
- `adjustment_type` (string): Filter by adjustment type (inventory, damage, theft, expired, other)
- `is_approved` (boolean): Filter by approval status
- `user` (int): Filter by user ID
- `date_from` (date): Filter adjustments from date (YYYY-MM-DD)
- `date_to` (date): Filter adjustments to date (YYYY-MM-DD)
- `search` (string): Search in product name, variant name, reason
- `ordering` (string): Order by field (created_at, adjustment_quantity)

**Response (200 OK):**
```json
{
    "count": 75,
    "next": "http://localhost:8000/api/stock/adjustments/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "product_name": "iPhone 15",
            "variant_name": "128GB Noir",
            "adjustment_type": "inventory",
            "quantity_before": 100,
            "quantity_after": 95,
            "adjustment_quantity": -5,
            "user_name": "Admin User",
            "is_approved": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Stock Adjustment Details
**Endpoint:** `GET /api/stock/adjustments/{id}/`

**Required Permission:** `stock_adjustments_manage`

**Response (200 OK):**
```json
{
    "id": 1,
    "product": 1,
    "product_name": "iPhone 15",
    "variant": 1,
    "variant_name": "128GB Noir",
    "adjustment_type": "inventory",
    "quantity_before": 100,
    "quantity_after": 95,
    "adjustment_quantity": -5,
    "reason": "Inventaire physique - 5 unités manquantes",
    "user": 1,
    "user_name": "Admin User",
    "is_approved": false,
    "approved_by": null,
    "approved_by_name": null,
    "approved_at": null,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Stock Adjustment
**Endpoint:** `POST /api/stock/adjustments/`

**Required Permission:** `stock_adjustments_manage`

**Request Body:**
```json
{
    "product": 1,
    "variant": 1,
    "adjustment_type": "inventory",
    "quantity_before": 100,
    "quantity_after": 95,
    "reason": "Inventaire physique - 5 unités manquantes"
}
```

**Response (201 Created):** Same as Get Stock Adjustment Details

### 4. Update Stock Adjustment
**Endpoint:** `PUT /api/stock/adjustments/{id}/` or `PATCH /api/stock/adjustments/{id}/`

**Required Permission:** `stock_adjustments_manage`

**Request Body (PATCH - Partial Update):**
```json
{
    "quantity_after": 98,
    "reason": "Inventaire corrigé - 2 unités retrouvées"
}
```

**Response (200 OK):** Same as Get Stock Adjustment Details

### 5. Delete Stock Adjustment
**Endpoint:** `DELETE /api/stock/adjustments/{id}/`

**Required Permission:** `stock_adjustments_manage`

**Response (204 No Content):** Empty response body

### 6. Stock Adjustment Filtering

#### Pending Approval
**Endpoint:** `GET /api/stock/adjustments/pending_approval/`

**Required Permission:** `stock_adjustments_manage`

**Description:** List adjustments pending approval

**Response (200 OK):** List of pending adjustments

### 7. Stock Adjustment Approval

#### Approve Adjustment
**Endpoint:** `POST /api/stock/adjustments/{id}/approve/`

**Required Permission:** `stock_adjustments_manage`

**Response (200 OK):** Updated adjustment details

#### Reject Adjustment
**Endpoint:** `POST /api/stock/adjustments/{id}/reject/`

**Required Permission:** `stock_adjustments_manage`

**Response (200 OK):** Updated adjustment details

### 8. Stock Adjustments Summary
**Endpoint:** `GET /api/stock/adjustments/summary/`

**Required Permission:** `stock_adjustments_manage`

**Description:** Get comprehensive adjustment statistics.

**Response (200 OK):**
```json
{
    "total_adjustments": 75,
    "pending_approval": 12,
    "approved": 63,
    "by_type": [
        {"adjustment_type": "inventory", "count": 45},
        {"adjustment_type": "damage", "count": 15},
        {"adjustment_type": "theft", "count": 10},
        {"adjustment_type": "expired", "count": 5}
    ]
}
```

---

## 🚨 Stock Alerts Management

### 1. List Stock Alerts
**Endpoint:** `GET /api/stock/alerts/`

**Description:** Retrieve all stock alerts with optional filtering and pagination.

**Required Permission:** `stock_alerts_manage`

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `product` (int): Filter by product ID
- `variant` (int): Filter by variant ID
- `alert_type` (string): Filter by alert type (low_stock, out_of_stock, overstock)
- `is_active` (boolean): Filter by active status
- `is_resolved` (boolean): Filter by resolved status
- `search` (string): Search in product name, variant name
- `ordering` (string): Order by field (created_at, current_quantity, threshold_quantity)

**Response (200 OK):**
```json
{
    "count": 30,
    "next": "http://localhost:8000/api/stock/alerts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "product_name": "iPhone 15",
            "variant_name": "128GB Noir",
            "alert_type": "low_stock",
            "current_quantity": 5,
            "threshold_quantity": 10,
            "is_active": true,
            "is_resolved": false,
            "is_low_stock": true,
            "is_out_of_stock": false,
            "is_overstock": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Stock Alert Details
**Endpoint:** `GET /api/stock/alerts/{id}/`

**Required Permission:** `stock_alerts_manage`

**Response (200 OK):**
```json
{
    "id": 1,
    "product": 1,
    "product_name": "iPhone 15",
    "variant": 1,
    "variant_name": "128GB Noir",
    "alert_type": "low_stock",
    "current_quantity": 5,
    "threshold_quantity": 10,
    "is_active": true,
    "is_resolved": false,
    "resolved_at": null,
    "resolved_by": null,
    "resolved_by_name": null,
    "is_low_stock": true,
    "is_out_of_stock": false,
    "is_overstock": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Stock Alert
**Endpoint:** `POST /api/stock/alerts/`

**Required Permission:** `stock_alerts_manage`

**Request Body:**
```json
{
    "product": 1,
    "variant": 1,
    "alert_type": "low_stock",
    "current_quantity": 5,
    "threshold_quantity": 10
}
```

**Response (201 Created):** Same as Get Stock Alert Details

### 4. Update Stock Alert
**Endpoint:** `PUT /api/stock/alerts/{id}/` or `PATCH /api/stock/alerts/{id}/`

**Required Permission:** `stock_alerts_manage`

**Request Body (PATCH - Partial Update):**
```json
{
    "threshold_quantity": 15,
    "is_active": false
}
```

**Response (200 OK):** Same as Get Stock Alert Details

### 5. Delete Stock Alert
**Endpoint:** `DELETE /api/stock/alerts/{id}/`

**Required Permission:** `stock_alerts_manage`

**Response (204 No Content):** Empty response body

### 6. Stock Alert Filtering

#### Active Alerts
**Endpoint:** `GET /api/stock/alerts/active/`

**Required Permission:** `stock_alerts_manage`

**Description:** List only active and unresolved alerts

**Response (200 OK):** List of active alerts

#### Resolved Alerts
**Endpoint:** `GET /api/stock/alerts/resolved/`

**Required Permission:** `stock_alerts_manage`

**Description:** List only resolved alerts

**Response (200 OK):** List of resolved alerts

### 7. Stock Alert Resolution

#### Resolve Alert
**Endpoint:** `POST /api/stock/alerts/{id}/resolve/`

**Required Permission:** `stock_alerts_manage`

**Response (200 OK):** Updated alert details

### 8. Stock Alerts Summary
**Endpoint:** `GET /api/stock/alerts/summary/`

**Required Permission:** `stock_alerts_manage`

**Description:** Get comprehensive alert statistics.

**Response (200 OK):**
```json
{
    "total_alerts": 30,
    "active_alerts": 8,
    "resolved_alerts": 22,
    "by_type": [
        {"alert_type": "low_stock", "count": 20},
        {"alert_type": "out_of_stock", "count": 8},
        {"alert_type": "overstock", "count": 2}
    ]
}
```

---

## 📊 Stock Reports Management

### 1. List Stock Reports
**Endpoint:** `GET /api/stock/reports/`

**Description:** Retrieve all stock reports with optional filtering and pagination.

**Required Permission:** `stock_reports_manage`

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `report_type` (string): Filter by report type (inventory, movements, adjustments, alerts, summary)
- `is_generated` (boolean): Filter by generation status
- `user` (int): Filter by user ID
- `date_from` (date): Filter reports from date (YYYY-MM-DD)
- `date_to` (date): Filter reports to date (YYYY-MM-DD)
- `search` (string): Search in title, description
- `ordering` (string): Order by field (created_at, generated_at)

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/stock/reports/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "report_type": "inventory",
            "title": "Rapport d'inventaire mensuel",
            "description": "Rapport complet de l'inventaire pour janvier 2024",
            "date_from": "2024-01-01",
            "date_to": "2024-01-31",
            "user_name": "Admin User",
            "is_generated": true,
            "generated_at": "2024-02-01T09:00:00Z",
            "period_days": 31,
            "created_at": "2024-01-31T18:00:00Z"
        }
    ]
}
```

### 2. Get Stock Report Details
**Endpoint:** `GET /api/stock/reports/{id}/`

**Required Permission:** `stock_reports_manage`

**Response (200 OK):**
```json
{
    "id": 1,
    "report_type": "inventory",
    "title": "Rapport d'inventaire mensuel",
    "description": "Rapport complet de l'inventaire pour janvier 2024",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "filters": {
        "product_categories": ["electronics", "accessories"],
        "warehouses": ["main", "secondary"]
    },
    "data": {
        "generated_at": "2024-02-01T09:00:00Z",
        "status": "success",
        "message": "Rapport généré avec succès",
        "summary": {
            "total_products": 150,
            "total_value": 250000.00,
            "low_stock_items": 12
        }
    },
    "user": 1,
    "user_name": "Admin User",
    "is_generated": true,
    "generated_at": "2024-02-01T09:00:00Z",
    "period_days": 31,
    "created_at": "2024-01-31T18:00:00Z",
    "updated_at": "2024-02-01T09:00:00Z"
}
```

### 3. Create Stock Report
**Endpoint:** `POST /api/stock/reports/`

**Required Permission:** `stock_reports_manage`

**Request Body:**
```json
{
    "report_type": "inventory",
    "title": "Rapport d'inventaire mensuel",
    "description": "Rapport complet de l'inventaire pour janvier 2024",
    "date_from": "2024-01-01",
    "date_to": "2024-01-31",
    "filters": {
        "product_categories": ["electronics", "accessories"],
        "warehouses": ["main", "secondary"]
    }
}
```

**Response (201 Created):** Same as Get Stock Report Details

### 4. Update Stock Report
**Endpoint:** `PUT /api/stock/reports/{id}/` or `PATCH /api/stock/reports/{id}/`

**Required Permission:** `stock_reports_manage`

**Request Body (PATCH - Partial Update):**
```json
{
    "title": "Rapport d'inventaire mensuel - Janvier 2024",
    "description": "Rapport mis à jour avec les dernières données"
}
```

**Response (200 OK):** Same as Get Stock Report Details

### 5. Delete Stock Report
**Endpoint:** `DELETE /api/stock/reports/{id}/`

**Required Permission:** `stock_reports_manage`

**Response (204 No Content):** Empty response body

### 6. Stock Report Generation

#### Generate Report
**Endpoint:** `POST /api/stock/reports/{id}/generate/`

**Required Permission:** `stock_reports_manage`

**Response (200 OK):** Updated report with generated data

### 7. Stock Reports Summary
**Endpoint:** `GET /api/stock/reports/summary/`

**Required Permission:** `stock_reports_manage`

**Description:** Get comprehensive report statistics.

**Response (200 OK):**
```json
{
    "total_reports": 25,
    "generated_reports": 20,
    "pending_reports": 5,
    "by_type": [
        {"report_type": "inventory", "count": 10},
        {"report_type": "movements", "count": 8},
        {"report_type": "adjustments", "count": 4},
        {"report_type": "alerts", "count": 2},
        {"report_type": "summary", "count": 1}
    ]
}
```

---

## 📈 Stock Analytics

### 1. Stock Movements Summary for Dashboard
**Endpoint:** `GET /api/stock/movements/summary/`

**Description:** Get comprehensive stock movement statistics for dashboard.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "movements": {
            "total": 250,
            "in": 120,
            "out": 130,
            "adjustment": 0,
            "recent": 45
        },
        "stock": {
            "total_value": 400000.00,
            "products_count": 150,
            "out_of_stock": 8
        },
        "alerts": {
            "low_stock": 12,
            "out_of_stock": 8,
            "total": 20
        },
        "recent_activity": {
            "movements_count": 45,
            "value": 25000.00
        }
    }
}
```

### 2. Test Stock Endpoint
**Endpoint:** `GET /api/stock/test/` or `POST /api/stock/test/`

**Description:** Test endpoint to verify stock API functionality.

**Response (200 OK):**
```json
{
    "message": "API Stock fonctionne correctement !",
    "endpoints": [
        "GET /api/stock/movements/ - Lister les mouvements",
        "POST /api/stock/movements/ - Créer un mouvement",
        "GET /api/stock/adjustments/ - Lister les ajustements",
        "POST /api/stock/adjustments/ - Créer un ajustement",
        "GET /api/stock/alerts/ - Lister les alertes",
        "GET /api/stock/reports/ - Lister les rapports"
    ]
}
```

---

## ❌ Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
    "error": "Validation Error",
    "details": {
        "quantity": ["La quantité ne peut pas être zéro."],
        "unit_cost": ["Le coût unitaire doit être positif."]
    }
}
```

**401 Unauthorized:**
```json
{
    "error": "Authentication credentials were not provided.",
    "detail": "Authentication credentials were not provided."
}
```

**403 Forbidden:**
```json
{
    "error": "Permission refusée",
    "detail": "Vous n'avez pas la permission de voir les mouvements de stock",
    "required_permission": "stock_movements_view"
}
```

**404 Not Found:**
```json
{
    "error": "Not found.",
    "detail": "Not found."
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal Server Error",
    "detail": "An error occurred while processing your request."
}
```

---

## 📊 Data Models

### Stock Movement Types
- `in`: Entrée
- `out`: Sortie
- `adjustment`: Ajustement
- `transfer`: Transfert
- `return`: Retour

### Stock Adjustment Types
- `inventory`: Inventaire
- `damage`: Dégâts
- `theft`: Vol
- `expired`: Périmé
- `other`: Autre

### Stock Alert Types
- `low_stock`: Stock bas
- `out_of_stock`: Rupture de stock
- `overstock`: Surstock

### Stock Report Types
- `inventory`: Inventaire
- `movements`: Mouvements
- `adjustments`: Ajustements
- `alerts`: Alertes
- `summary`: Résumé

### Field Validations

**StockMovement:**
- `quantity`: Cannot be zero
- `unit_cost`: Must be positive (optional)
- `product`: Required
- `variant`: Must belong to the product (if provided)

**StockAdjustment:**
- `quantity_after`: Must be non-negative
- `quantity_before`: Must be non-negative
- `product`: Required
- `variant`: Must belong to the product (if provided)

**StockAlert:**
- `current_quantity`: Must be non-negative
- `threshold_quantity`: Must be non-negative
- `product`: Required
- `variant`: Must belong to the product (if provided)

**StockReport:**
- `date_to`: Must be after date_from
- `report_type`: Required
- `title`: Required

---

## 🚀 Usage Examples

### JavaScript/Fetch Examples

**Get all stock movements:**
```javascript
const response = await fetch('/api/stock/movements/', {
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```

**Create a new stock movement:**
```javascript
const response = await fetch('/api/stock/movements/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        product: 1,
        variant: 1,
        movement_type: 'in',
        quantity: 50,
        unit_cost: 800.00,
        reference: 'PO-2024-001',
        notes: 'Réception de la commande fournisseur'
    })
});
const movement = await response.json();
```

**Approve a stock movement:**
```javascript
const response = await fetch('/api/stock/movements/1/approve/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const movement = await response.json();
```

**Create a stock adjustment:**
```javascript
const response = await fetch('/api/stock/adjustments/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        product: 1,
        variant: 1,
        adjustment_type: 'inventory',
        quantity_before: 100,
        quantity_after: 95,
        reason: 'Inventaire physique - 5 unités manquantes'
    })
});
const adjustment = await response.json();
```

**Resolve a stock alert:**
```javascript
const response = await fetch('/api/stock/alerts/1/resolve/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const alert = await response.json();
```

### cURL Examples

**Get stock movements:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/stock/movements/
```

**Create a stock movement:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"product": 1, "variant": 1, "movement_type": "in", "quantity": 50, "unit_cost": "800.00", "reference": "PO-2024-001"}' \
     http://localhost:8000/api/stock/movements/
```

**Get stock summary:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/stock/movements/summary/
```

**Generate a stock report:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/stock/reports/1/generate/
```

---

## 📝 Notes

1. **Automatic Calculations**: Total costs are calculated automatically when unit cost and quantity are provided
2. **Approval Workflow**: Stock movements and adjustments can require approval before being applied
3. **Permissions**: Each endpoint requires specific permissions for different actions
4. **Date Formats**: All dates are in ISO 8601 format (UTC)
5. **Validation**: All quantity fields are validated for appropriate values
6. **Relationships**: Movements and adjustments are linked to products and variants
7. **Alert System**: Stock alerts are automatically generated based on threshold quantities
8. **Report Generation**: Reports can be generated on-demand with custom filters

---

## 🔐 Required Permissions

### Stock Movements
- `stock_movements_view`: View stock movements
- `stock_movements_create`: Create, update, delete, and approve stock movements

### Stock Adjustments
- `stock_adjustments_manage`: Full management of stock adjustments

### Stock Alerts
- `stock_alerts_manage`: Full management of stock alerts

### Stock Reports
- `stock_reports_manage`: Full management of stock reports

---

**🎉 Your Stock APIs are ready for integration!**

This comprehensive API specification covers all stock management functionality in the Baobab ERP system, including movements, adjustments, alerts, and reports with full CRUD operations, approval workflows, and advanced filtering capabilities.
