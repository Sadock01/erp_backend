# API Dashboard - Spécifications Frontend

## Endpoints

### 1. Dashboard Complet (Recommandé)

**Endpoint:** `GET /api/dashboard/overview/`

**Headers:**
```
Authorization: Token <token_utilisateur>
Content-Type: application/json
```

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": {
        "kpis": {
            "revenue": {
                "today": 1500.00,
                "week": 10500.00,
                "month": 45000.00,
                "growth": 12.5
            },
            "orders": {
                "total": 150,
                "pending": 12,
                "confirmed": 45,
                "shipped": 38,
                "delivered": 55
            },
            "invoices": {
                "total": 120,
                "paid": 95,
                "pending": 25,
                "overdue": 5,
                "total_amount": 45000.00
            },
            "stock": {
                "total_value": 125000.00,
                "products_count": 250,
                "low_stock_alerts": 8,
                "out_of_stock": 2
            }
        },
        "sales_chart": {
            "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun"],
            "datasets": [
                {
                    "label": "Ventes",
                    "data": [12000, 15000, 18000, 22000, 19000, 25000],
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)"
                }
            ]
        },
        "products_chart": {
            "labels": ["Produit A", "Produit B", "Produit C", "Produit D"],
            "datasets": [
                {
                    "label": "Quantité vendue",
                    "data": [45, 32, 28, 15],
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.2)",
                        "rgba(54, 162, 235, 0.2)",
                        "rgba(255, 205, 86, 0.2)",
                        "rgba(75, 192, 192, 0.2)"
                    ]
                }
            ]
        },
        "clients_chart": {
            "labels": ["Nouveaux", "Réguliers", "VIP"],
            "datasets": [
                {
                    "label": "Nombre de clients",
                    "data": [12, 25, 8],
                    "backgroundColor": [
                        "rgba(255, 99, 132, 0.2)",
                        "rgba(54, 162, 235, 0.2)",
                        "rgba(255, 205, 86, 0.2)"
                    ]
                }
            ]
        },
        "alerts": [
            {
                "id": "stock_1",
                "type": "warning",
                "title": "Stock bas",
                "message": "iPhone 15 - Stock bas (3 unités restantes)",
                "priority": "high",
                "time": "Il y a 2 heures",
                "action_url": "/inventory/products/123/",
                "action_label": "Voir le produit",
                "created_at": "2024-01-15T10:30:00Z"
            }
        ],
        "recent_orders": [
            {
                "id": 1,
                "order_number": "CMD-2024-001",
                "customer_name": "Client ABC",
                "total_amount": 1250.00,
                "status": "pending",
                "created_at": "2024-01-15T09:15:00Z"
            }
        ],
        "recent_invoices": [
            {
                "id": 1,
                "invoice_number": "FAC-2024-001",
                "customer_name": "Client XYZ",
                "total_amount": 890.50,
                "status": "paid",
                "created_at": "2024-01-15T08:45:00Z"
            }
        ]
    }
}
```

---

### 2. KPIs du Dashboard

**Endpoint:** `GET /api/dashboard/kpis/`

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": {
        "total_orders": 150,
        "total_revenue": 125000.50,
        "total_customers": 45,
        "low_stock_alerts": 8
    }
}
```

---

### 3. Graphique des Ventes

**Endpoint:** `GET /api/dashboard/sales-chart/`

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": {
        "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun"],
        "datasets": [
            {
                "label": "Ventes",
                "data": [12000, 15000, 18000, 22000, 19000, 25000],
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)"
            }
        ]
    }
}
```

---

### 4. Top Produits

**Endpoint:** `GET /api/dashboard/top-products/`

**Paramètres optionnels:**
- `limit` (int) : Nombre de produits à retourner (défaut: 8)
- `period` (string) : Période (month, quarter, year) - défaut: month

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": {
        "labels": ["Produit A", "Produit B", "Produit C", "Produit D"],
        "datasets": [
            {
                "label": "Quantité vendue",
                "data": [45, 32, 28, 15],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 205, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)"
                ]
            }
        ]
    }
}
```

---

### 5. Répartition des Clients

**Endpoint:** `GET /api/dashboard/clients-distribution/`

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": {
        "labels": ["Nouveaux", "Réguliers", "VIP"],
        "datasets": [
            {
                "label": "Nombre de clients",
                "data": [12, 25, 8],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 205, 86, 0.2)"
                ]
            }
        ]
    }
}
```

---

### 6. Alertes

**Endpoint:** `GET /api/dashboard/alerts/`

**Paramètres optionnels:**
- `limit` (int) : Nombre d'alertes à retourner (défaut: 10)
- `priority` (string) : Filtre par priorité (high, medium, low, all) - défaut: all

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": [
        {
            "id": "stock_1",
            "type": "warning",
            "title": "Stock bas",
            "message": "iPhone 15 - Stock bas (3 unités restantes)",
            "priority": "high",
            "time": "Il y a 2 heures",
            "action_url": "/inventory/products/123/",
            "action_label": "Voir le produit",
            "created_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": "invoice_1",
            "type": "error",
            "title": "Facture en retard",
            "message": "Facture #FAC-2024-001 - Échéance dépassée de 5 jours",
            "priority": "high",
            "time": "Il y a 1 jour",
            "action_url": "/sales/invoices/123/",
            "action_label": "Voir la facture",
            "created_at": "2024-01-14T14:20:00Z"
        }
    ],
    "summary": {
        "total": 2,
        "high_priority": 2,
        "medium_priority": 0,
        "low_priority": 0
    }
}
```

---

### 7. Commandes Récentes

**Endpoint:** `GET /api/dashboard/recent-orders/`

**Paramètres optionnels:**
- `limit` (int) : Nombre de commandes à retourner (défaut: 10)
- `status` (string) : Filtre par statut (pending, confirmed, shipped, delivered) - défaut: all

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": [
        {
            "id": "CMD-2024-001",
            "customer": "Jean Dupont",
            "amount": 1250.00,
            "status": "confirmed",
            "date": "2024-01-15T09:15:00Z",
            "currency": "EUR"
        },
        {
            "id": "CMD-2024-002",
            "customer": "Marie Martin",
            "amount": 890.50,
            "status": "pending",
            "date": "2024-01-15T08:30:00Z",
            "currency": "EUR"
        }
    ],
    "summary": {
        "total": 2,
        "total_amount": 2140.50,
        "status_breakdown": {
            "confirmed": 1,
            "pending": 1
        }
    }
}
```

---

### 8. Factures Récentes

**Endpoint:** `GET /api/dashboard/recent-invoices/`

**Paramètres optionnels:**
- `limit` (int) : Nombre de factures à retourner (défaut: 10)
- `status` (string) : Filtre par statut (paid, pending, overdue) - défaut: all

**Réponse de Succès (200):**
```json
{
    "success": true,
    "data": [
        {
            "id": "FAC-2024-001",
            "customer": "Jean Dupont",
            "amount": 1250.00,
            "status": "paid",
            "due_date": "2024-01-10T00:00:00Z",
            "created_at": "2024-01-15T09:15:00Z"
        },
        {
            "id": "FAC-2024-002",
            "customer": "Marie Martin",
            "amount": 890.50,
            "status": "pending",
            "due_date": "2024-01-20T00:00:00Z",
            "created_at": "2024-01-15T08:45:00Z"
        }
    ],
    "summary": {
        "total": 2,
        "total_amount": 2140.50,
        "status_breakdown": {
            "paid": 1,
            "pending": 1
        }
    }
}
```

---

## Codes d'Erreur

**401 - Non autorisé:**
```json
{
    "detail": "Token d'authentification invalide."
}
```

**500 - Erreur serveur:**
```json
{
    "success": false,
    "error": {
        "code": "DASHBOARD_ERROR",
        "message": "Erreur lors de la récupération des données du dashboard"
    }
}
```

---

## Exemple d'Utilisation

```javascript
// Récupération du dashboard complet
async function fetchDashboardData(token) {
    const response = await fetch('/api/dashboard/overview/', {
        method: 'GET',
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    return data.success ? data.data : null;
}

// Récupération des KPIs uniquement
async function fetchKPIs(token) {
    const response = await fetch('/api/dashboard/kpis/', {
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    return data.success ? data.data : null;
}

// Graphique des ventes avec période
async function fetchSalesChart(token, period = 'month') {
    const response = await fetch(`/api/dashboard/sales-chart/?period=${period}`, {
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    return data.success ? data.data : null;
}

// Top produits avec limite
async function fetchTopProducts(token, limit = 8) {
    const response = await fetch(`/api/dashboard/top-products/?limit=${limit}`, {
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    return data.success ? data.data : null;
}
```

---

## Notes

- **Authentification requise:** Tous les endpoints nécessitent un token d'authentification
- **Format des dates:** ISO 8601
- **Monnaie:** Montants en euros (EUR)
- **Performance:** Utilisez `/api/dashboard/overview/` pour récupérer toutes les données en une seule requête
- **Paramètres:** Tous les endpoints supportent les paramètres `limit`, `period`, `status`, etc.
- **Types d'alertes:** `warning` (orange), `error` (rouge), `info` (bleu)
- **Priorités:** `high`, `medium`, `low`
