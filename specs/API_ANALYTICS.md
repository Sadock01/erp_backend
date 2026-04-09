# 📊 API Analytics - Documentation Complète

## 🌐 Base URL
```
http://localhost:8000/api/analytics/
```

---

## 📋 1. ENDPOINT PRINCIPAL - Données Complètes

### **GET** `/api/analytics/`
**Description :** Récupère toutes les données analytics (KPIs, graphiques, tableaux)

**Paramètres de requête :**
- `period` (string, optionnel) : `7d`, `30d`, `90d`, `1y` (défaut: `30d`)
- `custom_start_date` (string, optionnel) : Date de début (format: `YYYY-MM-DD`)
- `custom_end_date` (string, optionnel) : Date de fin (format: `YYYY-MM-DD`)
- `customer_segment` (string, optionnel) : `all`, `new`, `returning`, `vip`, `inactive` (défaut: `all`)
- `product_category` (string, optionnel) : `all`, `electronics`, `clothing`, `home`, `sports`, `books`, `beauty` (défaut: `all`)
- `revenue_min` (number, optionnel) : Montant minimum en FCFA (défaut: 0)
- `revenue_max` (number, optionnel) : Montant maximum en FCFA (défaut: 10000000)
- `turnover_min` (number, optionnel) : Rotation des stocks minimum (défaut: 0)
- `turnover_max` (number, optionnel) : Rotation des stocks maximum (défaut: 100)

**Réponse :**
```json
{
  "kpis": {
    "total_sales": 7800000,
    "sales_growth": 12.5,
    "avg_order_value": 125000,
    "aov_growth": 8.3,
    "customer_lifetime_value": 450000,
    "clv_growth": 15.2,
    "inventory_turnover": 4.2,
    "turnover_growth": -5.2
  },
  "revenue_chart": {
    "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "datasets": [{
      "label": "Revenus (FCFA)",
      "data": [1200000, 1350000, 1100000, 1500000, 1800000, 1650000, 1900000, 1750000, 2000000, 1850000, 2100000, 1950000]
    }]
  },
  "sales_performance_chart": {
    "labels": ["Électronique", "Vêtements", "Maison & Jardin", "Sport & Loisirs", "Livres & Médias", "Beauté & Santé"],
    "datasets": [{
      "label": "Chiffre d'affaires (FCFA)",
      "data": [2500000, 1800000, 1200000, 900000, 600000, 800000]
    }]
  },
  "top_customers": [
    {
      "rank": 1,
      "name": "SARL Tech Solutions",
      "total_orders": 45,
      "total_spent": 2500000,
      "last_order": "2024-01-15"
    }
  ],
  "top_products": [
    {
      "rank": 1,
      "name": "iPhone 15 Pro",
      "category": "Électronique",
      "sales": 2500000,
      "units_sold": 25
    }
  ]
}
```

---

## 📊 2. ENDPOINTS SPÉCIFIQUES

### **GET** `/api/analytics/kpis/`
**Description :** Récupère uniquement les KPIs
**Paramètres :** Identiques à l'endpoint principal
**Réponse :**
```json
{
  "total_sales": 7800000,
  "sales_growth": 12.5,
  "avg_order_value": 125000,
  "aov_growth": 8.3,
  "customer_lifetime_value": 450000,
  "clv_growth": 15.2,
  "inventory_turnover": 4.2,
  "turnover_growth": -5.2
}
```

### **GET** `/api/analytics/revenue-chart/`
**Description :** Récupère les données du graphique des revenus
**Paramètres :** Identiques à l'endpoint principal
**Réponse :**
```json
{
  "labels": ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun", "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"],
  "datasets": [{
    "label": "Revenus (FCFA)",
    "data": [1200000, 1350000, 1100000, 1500000, 1800000, 1650000, 1900000, 1750000, 2000000, 1850000, 2100000, 1950000]
  }]
}
```

### **GET** `/api/analytics/sales-performance/`
**Description :** Récupère les données de performance des ventes par catégorie
**Paramètres :** Identiques à l'endpoint principal
**Réponse :**
```json
{
  "labels": ["Électronique", "Vêtements", "Maison & Jardin", "Sport & Loisirs", "Livres & Médias", "Beauté & Santé"],
  "datasets": [{
    "label": "Chiffre d'affaires (FCFA)",
    "data": [2500000, 1800000, 1200000, 900000, 600000, 800000]
  }]
}
```

### **GET** `/api/analytics/top-customers/`
**Description :** Récupère le classement des meilleurs clients
**Paramètres :** Identiques à l'endpoint principal
**Réponse :**
```json
[
  {
    "rank": 1,
    "name": "SARL Tech Solutions",
    "total_orders": 45,
    "total_spent": 2500000,
    "last_order": "2024-01-15"
  }
]
```

### **GET** `/api/analytics/top-products/`
**Description :** Récupère le classement des meilleurs produits
**Paramètres :** Identiques à l'endpoint principal
**Réponse :**
```json
[
  {
    "rank": 1,
    "name": "iPhone 15 Pro",
    "category": "Électronique",
    "sales": 2500000,
    "units_sold": 25
  }
]
```

---

## 🔧 3. FILTRES ET OPTIONS

### **Périodes Supportées :**
- `7d` : 7 derniers jours
- `30d` : 30 derniers jours (défaut)
- `90d` : 3 derniers mois
- `1y` : 1 an
- `custom` : Période personnalisée (nécessite `custom_start_date` et `custom_end_date`)

### **Segments Clients :**
- `all` : Tous les clients (défaut)
- `new` : Nouveaux clients (dernière commande < 30 jours)
- `returning` : Clients récurrents (≥ 2 commandes)
- `vip` : Clients VIP (CA > 1M FCFA)
- `inactive` : Clients inactifs (dernière commande > 90 jours)

### **Catégories Produits :**
- `all` : Toutes les catégories (défaut)
- `electronics` : Électronique
- `clothing` : Vêtements
- `home` : Maison & Jardin
- `sports` : Sport & Loisirs
- `books` : Livres & Médias
- `beauty` : Beauté & Santé

### **Plages de Revenus :**
- `revenue_min` : Montant minimum en FCFA (0 par défaut)
- `revenue_max` : Montant maximum en FCFA (10,000,000 par défaut)

### **Plages de Rotation des Stocks :**
- `turnover_min` : Rotation minimum (0 par défaut)
- `turnover_max` : Rotation maximum (100 par défaut)

---

## 📈 4. MÉTRIQUES ET KPIs

### **Chiffre d'Affaires Total :**
- **Description** : Ventes totales sur la période
- **Unité** : FCFA
- **Calcul** : Somme de toutes les commandes validées

### **Croissance des Ventes :**
- **Description** : Évolution par rapport à la période précédente
- **Unité** : Pourcentage (%)
- **Calcul** : `((CA_actuel - CA_précédent) / CA_précédent) * 100`

### **Panier Moyen :**
- **Description** : Valeur moyenne par commande
- **Unité** : FCFA
- **Calcul** : `CA_total / nombre_commandes`

### **Valeur Client :**
- **Description** : Valeur vie client moyenne
- **Unité** : FCFA
- **Calcul** : `CA_total / nombre_clients_uniques`

### **Rotation des Stocks :**
- **Description** : Vitesse de rotation des stocks
- **Unité** : Nombre de fois (x)
- **Calcul** : `Coût_des_ventes / Stock_moyen`

---

## 🎯 5. GRAPHIQUES

### **Graphique des Revenus :**
- **Type** : Ligne avec remplissage
- **Données** : 12 mois de revenus
- **Couleur** : Bleu (#3B82F6)
- **Format** : Montants en FCFA

### **Graphique Performance des Ventes :**
- **Type** : Barres verticales
- **Données** : 6 catégories de produits
- **Couleurs** : Différentes par catégorie
- **Format** : Montants en FCFA

---

## 📋 6. TABLEAUX

### **Top Clients :**
- **Colonnes** : Rang, Nom, Commandes, Montant Total, Dernière Commande
- **Tri** : Par montant total décroissant
- **Limite** : 5 clients

### **Top Produits :**
- **Colonnes** : Rang, Produit, Catégorie, Ventes, Unités Vendues
- **Tri** : Par chiffre d'affaires décroissant
- **Limite** : 5 produits

---

## 🔐 7. AUTHENTIFICATION

**Tous les endpoints nécessitent :**
- **Header** : `Authorization: Token <token>`
- **Token** : Valide et non expiré
- **Permissions** : Aucune permission spéciale requise (accès libre pour tous les utilisateurs authentifiés)

---

## ⚡ 8. PERFORMANCE

### **Cache :**
- **Durée** : 5 minutes pour les KPIs
- **Durée** : 10 minutes pour les graphiques
- **Durée** : 15 minutes pour les tableaux

### **Pagination :**
- **Tableaux** : 50 éléments par page maximum
- **Paramètre** : `page` et `limit`

### **Limites :**
- **Période max** : 2 ans
- **Requêtes/min** : 100 par utilisateur
- **Timeout** : 30 secondes

---

## 🚨 9. GESTION D'ERREURS

### **Codes d'erreur :**
- `400` : Paramètres invalides
- `401` : Non authentifié
- `403` : Accès refusé
- `404` : Données non trouvées
- `429` : Trop de requêtes
- `500` : Erreur serveur

### **Format d'erreur :**
```json
{
  "error": {
    "code": "INVALID_PERIOD",
    "message": "Période invalide. Utilisez 7d, 30d, 90d, 1y ou custom",
    "details": {
      "field": "period",
      "value": "invalid"
    }
  }
}
```

---

## 📝 10. EXEMPLES D'UTILISATION

### **Requête simple :**
```bash
GET /api/analytics/?period=30d
```

### **Requête avec filtres :**
```bash
GET /api/analytics/?period=30d&customer_segment=vip&product_category=electronics&revenue_min=1000000
```

### **Requête période personnalisée :**
```bash
GET /api/analytics/?period=custom&custom_start_date=2024-01-01&custom_end_date=2024-01-31
```

---

## 🎨 11. NOTES D'IMPLÉMENTATION

### **Format des dates :**
- **Entrée** : `YYYY-MM-DD`
- **Sortie** : `YYYY-MM-DD`
- **Timezone** : UTC

### **Format des montants :**
- **Unité** : FCFA (Franc CFA)
- **Séparateur** : Espaces pour les milliers
- **Décimales** : 0 (nombres entiers)

### **Format des pourcentages :**
- **Décimales** : 1 chiffre après la virgule
- **Signe** : + pour les croissances, - pour les baisses

---

## 🧪 12. TESTS

### **Scripts de test disponibles :**
- `test_analytics_api.py` : Test de base des endpoints
- `test_analytics_advanced.py` : Test des paramètres et cas d'erreur
- `cleanup_analytics_test.py` : Nettoyage des données de test

### **Collection Postman :**
- `Postman_Analytics_Collection.json` : Collection complète pour Postman

---

**📊 Cette API Analytics est maintenant prête pour la production !**
