# 🏠 Spécification du Dashboard - Baobab ERP

## 🎯 Vue d'ensemble

Le dashboard (page d'accueil) de l'ERP Baobab doit offrir une vue d'ensemble complète et personnalisée des performances de l'entreprise. Il doit être adaptatif selon le rôle de l'utilisateur et fournir des KPIs en temps réel.

---

## 📊 Structure du Dashboard

### 1. **Header/Navigation** (Commun à tous)
- **Logo Baobab ERP**
- **Menu de navigation** principal
- **Profil utilisateur** avec rôle affiché
- **Notifications** en temps réel
- **Recherche globale** (produits, clients, commandes)
- **Sélecteur de période** (aujourd'hui, cette semaine, ce mois, personnalisé)

### 2. **Widgets principaux** (Selon les permissions)

---

## 🔥 Section 1 : KPIs Principaux (Top Row)

### 💰 **Chiffre d'Affaires**
- **API Source** : `/api/sales/orders/summary/`
- **Métriques** :
  - CA du jour/semaine/mois
  - Évolution vs période précédente (%)
  - CA par statut de commande
- **Visualisation** : Grand chiffre + graphique en barres
- **Couleur** : Vert (#28a745)

### 📦 **Commandes**
- **API Source** : `/api/sales/orders/summary/`
- **Métriques** :
  - Total commandes
  - Commandes en attente
  - Commandes confirmées
  - Commandes expédiées
  - Taux de conversion
- **Visualisation** : Cartes avec icônes + mini graphique
- **Couleur** : Bleu (#007bff)

### 💳 **Facturation**
- **API Source** : `/api/sales/invoices/summary/`
- **Métriques** :
  - Total factures
  - Montant total facturé
  - Montant encaissé
  - Montant en attente
  - Factures en retard
- **Visualisation** : Graphique en secteurs + indicateurs
- **Couleur** : Orange (#fd7e14)

### 📊 **Stock**
- **API Source** : `/api/stock/movements/summary/`
- **Métriques** :
  - Valeur totale du stock
  - Nombre de produits
  - Alertes de stock bas
  - Mouvements récents
- **Visualisation** : Graphique de tendance + alertes
- **Couleur** : Violet (#6f42c1)

---

## 📈 Section 2 : Graphiques et Analyses

### 📊 **Graphique des Ventes (Principale)**
- **API Source** : `/api/sales/orders/?date_from=X&date_to=Y`
- **Type** : Graphique linéaire ou en barres
- **Données** :
  - Évolution du CA sur la période sélectionnée
  - Comparaison avec période précédente
  - Ventes par jour/semaine/mois
- **Interactivité** : Zoom, filtres par statut

### 🏆 **Top Produits**
- **API Source** : `/api/sales/order-items/?ordering=-quantity`
- **Type** : Graphique en barres horizontales
- **Données** :
  - Top 10 des produits les plus vendus
  - Quantités vendues
  - Chiffre d'affaires par produit
- **Interactivité** : Clic pour voir les détails

### 👥 **Répartition des Clients**
- **API Source** : `/api/customers/?ordering=-created_at`
- **Type** : Graphique en secteurs
- **Données** :
  - Nouveaux clients vs existants
  - Répartition par pays/région
  - Clients actifs vs inactifs
- **Interactivité** : Drill-down par segment

### 📦 **État du Stock**
- **API Source** : `/api/stock/alerts/`
- **Type** : Graphique en barres empilées
- **Données** :
  - Produits en stock normal
  - Produits en stock bas
  - Produits en rupture
  - Valeur par catégorie
- **Interactivité** : Filtres par catégorie

---

## 🚨 Section 3 : Alertes et Notifications

### ⚠️ **Alertes Urgentes**
- **API Source** : `/api/stock/alerts/`
- **Types d'alertes** :
  - Stock bas (seuil critique)
  - Factures en retard
  - Commandes en attente de validation
  - Produits en rupture
- **Affichage** : Liste déroulante avec badges de priorité
- **Actions** : Boutons d'action rapide

### 📋 **Tâches en Attente**
- **API Source** : Divers endpoints selon le rôle
- **Types** :
  - Commandes à confirmer
  - Factures à envoyer
  - Mouvements de stock à approuver
  - Clients à contacter
- **Affichage** : Liste avec priorité et délai

---

## 📋 Section 4 : Tableaux de Données

### 🛒 **Commandes Récentes**
- **API Source** : `/api/sales/orders/?ordering=-created_at&limit=10`
- **Colonnes** :
  - Numéro commande
  - Client
  - Montant
  - Statut
  - Date
  - Actions
- **Fonctionnalités** : Tri, filtres, actions rapides

### 💰 **Factures Récentes**
- **API Source** : `/api/sales/invoices/?ordering=-created_at&limit=10`
- **Colonnes** :
  - Numéro facture
  - Client
  - Montant
  - Statut
  - Échéance
  - Actions
- **Fonctionnalités** : Tri, filtres, génération PDF

### 📦 **Mouvements de Stock Récents**
- **API Source** : `/api/stock/movements/?ordering=-created_at&limit=10`
- **Colonnes** :
  - Produit
  - Type de mouvement
  - Quantité
  - Coût
  - Référence
  - Date
- **Fonctionnalités** : Filtres par type, tri

---

## 👥 Section 5 : Informations Utilisateur

### 🎭 **Profil et Rôle**
- **API Source** : `/api/auth/profile/` + `/api/permissions/user-permissions/{user_id}/`
- **Informations** :
  - Nom et prénom
  - Rôle actuel
  - Permissions accordées
  - Dernière connexion
- **Actions** : Déconnexion, changement de mot de passe

### 📊 **Statistiques Personnelles**
- **API Source** : Filtrage des données par utilisateur
- **Métriques** :
  - Commandes créées
  - Factures générées
  - Clients ajoutés
  - Performance vs objectifs
- **Visualisation** : Graphiques personnalisés

---

## 🔧 Section 6 : Outils et Actions Rapides

### ⚡ **Actions Rapides**
- **Créer une commande**
- **Créer un devis**
- **Ajouter un client**
- **Créer un mouvement de stock**
- **Générer un rapport**
- **Exporter des données**

### 🔍 **Recherche Globale**
- **API Source** : Endpoints de recherche de chaque module
- **Types de recherche** :
  - Produits par nom/SKU
  - Clients par nom/email
  - Commandes par numéro
  - Factures par numéro
- **Affichage** : Résultats en temps réel avec suggestions

---

## 📱 Responsive Design

### 🖥️ **Desktop (1200px+)**
- 4 colonnes pour les KPIs principaux
- 2 colonnes pour les graphiques
- Sidebar pour les alertes
- Tableaux complets

### 📱 **Tablet (768px - 1199px)**
- 2 colonnes pour les KPIs
- 1 colonne pour les graphiques
- Sidebar rétractable
- Tableaux avec pagination

### 📱 **Mobile (< 768px)**
- 1 colonne pour tous les éléments
- Navigation en accordéon
- Tableaux en mode carte
- Actions rapides en bas

---

## 🎨 Thème et Personnalisation

### 🌈 **Couleurs par Module**
- **Ventes** : Bleu (#007bff)
- **Clients** : Vert (#28a745)
- **Stock** : Violet (#6f42c1)
- **Factures** : Orange (#fd7e14)
- **Permissions** : Rouge (#dc3545)
- **Inventaire** : Teal (#20c997)

### 🎯 **Personnalisation par Rôle**

#### 🔴 **Super Admin**
- Accès à tous les widgets
- Statistiques système
- Gestion des utilisateurs
- Logs de sécurité

#### 🟠 **Manager**
- KPIs de performance
- Rapports d'équipe
- Alertes de gestion
- Analyses avancées

#### 🟡 **Sales**
- Focus sur les ventes
- Pipeline des commandes
- Objectifs de vente
- Clients à contacter

#### 🟢 **Stock Manager**
- Focus sur l'inventaire
- Alertes de stock
- Mouvements récents
- Rapports de stock

#### 🔵 **Viewer**
- Données en lecture seule
- Rapports limités
- Pas d'actions de modification

---

## 🔄 Actualisation et Performance

### ⏱️ **Fréquence d'Actualisation**
- **Données critiques** : 30 secondes
- **Graphiques** : 1 minute
- **Tableaux** : 2 minutes
- **Statistiques** : 5 minutes

### 🚀 **Optimisations**
- **Cache** : Mise en cache des données fréquentes
- **Pagination** : Chargement progressif des tableaux
- **Lazy loading** : Chargement à la demande
- **Websockets** : Notifications en temps réel

---

## 📊 APIs Spécifiques pour le Dashboard

### 🎯 **Endpoint Dashboard Principal**
```http
GET /api/dashboard/
Authorization: Token <votre_token>
```

**Réponse attendue :**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "role": "Sales Manager",
    "permissions": [...]
  },
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
  "charts": {
    "sales_trend": [...],
    "top_products": [...],
    "customers_distribution": [...],
    "stock_status": [...]
  },
  "alerts": [
    {
      "type": "stock_low",
      "message": "iPhone 15 - Stock bas (3 unités)",
      "priority": "high",
      "action_url": "/inventory/products/123/"
    }
  ],
  "recent_activities": [
    {
      "type": "order_created",
      "message": "Nouvelle commande #CMD-001",
      "time": "2024-01-15T10:30:00Z",
      "user": "John Doe"
    }
  ]
}
```

### 📈 **Endpoints de Données Détaillées**

| Widget | Endpoint | Description |
|--------|----------|-------------|
| **KPIs Ventes** | `/api/sales/orders/summary/` | Statistiques des commandes |
| **KPIs Factures** | `/api/sales/invoices/summary/` | Statistiques des factures |
| **KPIs Stock** | `/api/stock/movements/summary/` | Statistiques du stock |
| **Graphique Ventes** | `/api/sales/orders/?date_from=X&date_to=Y` | Données temporelles |
| **Top Produits** | `/api/sales/order-items/?ordering=-quantity` | Produits populaires |
| **Alertes** | `/api/stock/alerts/` | Alertes de stock |
| **Activités** | `/api/permissions/logs/recent/` | Logs récents |

---

## 🛠️ Implémentation Technique

### 🎨 **Frontend**
- **Framework** : React/Vue.js/Angular
- **UI Library** : Bootstrap/Material-UI/Ant Design
- **Charts** : Chart.js/D3.js/Recharts
- **State Management** : Redux/Vuex/NgRx

### 🔧 **Backend**
- **Endpoint principal** : `/api/dashboard/`
- **Cache** : Redis pour les données fréquentes
- **Websockets** : Pour les notifications temps réel
- **Permissions** : Vérification des droits d'accès

### 📱 **Fonctionnalités Avancées**
- **Export PDF** : Rapports du dashboard
- **Export Excel** : Données des tableaux
- **Notifications push** : Alertes importantes
- **Mode sombre** : Thème alternatif
- **Personnalisation** : Widgets configurables

---

## 🎯 Objectifs du Dashboard

### 📊 **Pour les Managers**
- Vue d'ensemble des performances
- Identification des tendances
- Prise de décision éclairée
- Suivi des objectifs

### 👨‍💼 **Pour les Utilisateurs**
- Accès rapide aux informations
- Actions courantes simplifiées
- Alertes personnalisées
- Productivité améliorée

### 🏢 **Pour l'Entreprise**
- Transparence des données
- Amélioration de la performance
- Réduction des erreurs
- Optimisation des processus

---

## 🚀 Roadmap d'Implémentation

### **Phase 1** : Structure de base
- [ ] Layout responsive
- [ ] KPIs principaux
- [ ] Authentification et permissions

### **Phase 2** : Données et graphiques
- [ ] Intégration des APIs
- [ ] Graphiques interactifs
- [ ] Actualisation automatique

### **Phase 3** : Fonctionnalités avancées
- [ ] Alertes en temps réel
- [ ] Personnalisation par rôle
- [ ] Export et rapports

### **Phase 4** : Optimisations
- [ ] Performance et cache
- [ ] Notifications push
- [ ] Mode hors ligne

---

## 📝 Conclusion

Le dashboard de l'ERP Baobab doit être un véritable centre de contrôle pour l'entreprise, offrant une vue d'ensemble claire et des outils d'action rapide. Il doit s'adapter aux différents rôles et fournir les informations les plus pertinentes pour chaque utilisateur.

**Points clés :**
- ✅ **Personnalisation** selon le rôle utilisateur
- ✅ **Temps réel** pour les données critiques
- ✅ **Responsive** pour tous les appareils
- ✅ **Intuitif** et facile à utiliser
- ✅ **Performant** avec mise en cache
- ✅ **Extensible** pour de futures fonctionnalités
