# API Inventory - Documentation

## Endpoints disponibles

### Base URL
```
/api/inventory/
```

## 1. **Catégories** - `/api/inventory/categories/`

### **GET /api/inventory/categories/**
- **Description** : Liste toutes les catégories
- **Paramètres** :
  - `is_active` : Filtre par statut actif (true/false)
  - `parent` : Filtre par catégorie parente
  - `search` : Recherche dans nom et description
  - `ordering` : Tri (name, sort_order, created_at)

### **POST /api/inventory/categories/**
- **Description** : Créer une nouvelle catégorie
- **Body** :
```json
{
  "name": "Électronique",
  "description": "Appareils électroniques",
  "parent": null,
  "is_active": true,
  "sort_order": 1
}
```

### **Actions spéciales :**
- **GET /api/inventory/categories/active/** : Catégories actives
- **GET /api/inventory/categories/{id}/products/** : Produits d'une catégorie

## 2. **Produits** - `/api/inventory/products/`

### **GET /api/inventory/products/**
- **Description** : Liste tous les produits
- **Paramètres** :
  - `status` : Filtre par statut (active, inactive, discontinued, out_of_stock)
  - `product_type` : Filtre par type (simple, variable, bundle)
  - `category` : Filtre par catégorie
  - `is_digital` : Filtre par type numérique (true/false)
  - `is_featured` : Filtre par produits vedettes (true/false)
  - `min_price` / `max_price` : Filtre par prix
  - `in_stock` : Filtre par disponibilité (true/false)
  - `search` : Recherche dans nom, description, SKU, code-barres, tags

### **POST /api/inventory/products/**
- **Description** : Créer un nouveau produit
- **Body** :
```json
{
  "name": "iPhone 15",
  "description": "Dernier iPhone d'Apple",
  "short_description": "iPhone 15 128GB",
  "sku": "IPH15-128",
  "barcode": "1234567890123",
  "category": 1,
  "product_type": "variable",
  "status": "active",
  "price": "999.99",
  "cost_price": "600.00",
  "weight": "0.174",
  "dimensions": "147.6 x 71.6 x 7.8 mm",
  "is_digital": false,
  "is_featured": true,
  "tags": "smartphone, apple, ios",
  "meta_title": "iPhone 15 - Apple",
  "meta_description": "Découvrez le nouvel iPhone 15"
}
```

### **Actions spéciales :**
- **GET /api/inventory/products/active/** : Produits actifs
- **GET /api/inventory/products/featured/** : Produits vedettes
- **GET /api/inventory/products/search/?q=terme** : Recherche avancée
- **GET /api/inventory/products/{id}/variants/** : Variants d'un produit

## 3. **Variants** - `/api/inventory/variants/`

### **GET /api/inventory/variants/**
- **Description** : Liste tous les variants
- **Paramètres** :
  - `product` : Filtre par produit
  - `variant_type` : Filtre par type (size, color, material, style, other)
  - `is_active` : Filtre par statut actif

### **POST /api/inventory/variants/**
- **Description** : Créer un nouveau variant
- **Body** :
```json
{
  "product": 1,
  "name": "Rouge - 128GB",
  "sku": "IPH15-128-RED",
  "variant_type": "color",
  "value": "Rouge",
  "price_modifier": "0.00",
  "stock_quantity": 50,
  "min_stock_level": 5,
  "max_stock_level": 100,
  "is_active": true,
  "sort_order": 1
}
```

## Exemples d'utilisation Postman

### 1. Créer une catégorie
```bash
POST http://localhost:8000/api/inventory/categories/
Authorization: Token VOTRE_TOKEN
Content-Type: application/json

{
  "name": "Smartphones",
  "description": "Téléphones intelligents",
  "is_active": true,
  "sort_order": 1
}
```

### 2. Créer un produit
```bash
POST http://localhost:8000/api/inventory/products/
Authorization: Token VOTRE_TOKEN
Content-Type: application/json

{
  "name": "Samsung Galaxy S24",
  "description": "Dernier smartphone Samsung",
  "sku": "SGS24-256",
  "category": 1,
  "product_type": "variable",
  "status": "active",
  "price": "899.99",
  "is_featured": true
}
```

### 3. Créer un variant
```bash
POST http://localhost:8000/api/inventory/variants/
Authorization: Token VOTRE_TOKEN
Content-Type: application/json

{
  "product": 1,
  "name": "Noir - 256GB",
  "sku": "SGS24-256-BLK",
  "variant_type": "color",
  "value": "Noir",
  "stock_quantity": 25,
  "min_stock_level": 3
}
```

### 4. Lister les produits actifs
```bash
GET http://localhost:8000/api/inventory/products/active/
Authorization: Token VOTRE_TOKEN
```

### 5. Rechercher des produits
```bash
GET http://localhost:8000/api/inventory/products/search/?q=iphone
Authorization: Token VOTRE_TOKEN
```

### 6. Filtres avancés
```bash
GET http://localhost:8000/api/inventory/products/?category=1&min_price=500&max_price=1000&is_featured=true
Authorization: Token VOTRE_TOKEN
```

## Codes de réponse

- **200** : Succès
- **201** : Créé avec succès
- **400** : Erreur de validation
- **401** : Non authentifié
- **403** : Non autorisé
- **404** : Ressource non trouvée
- **500** : Erreur serveur

## Authentification

L'API utilise l'authentification par token Django REST Framework. Incluez le token dans l'en-tête :

```
Authorization: Token VOTRE_TOKEN
```

## Fonctionnalités avancées

### Gestion des images
- Upload d'images pour les produits
- Image principale automatique
- Aperçu des images dans l'admin

### Gestion des variants
- Types de variants configurables
- Prix modifiables par variant
- Gestion des stocks par variant

### Recherche et filtres
- Recherche textuelle avancée
- Filtres multiples
- Tri personnalisable
- Pagination automatique
