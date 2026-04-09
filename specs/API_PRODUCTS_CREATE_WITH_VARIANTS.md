# API Création de Produit avec Variants

## Endpoint
```
POST /api/inventory/products/with-variants/
```

## Description
Crée un produit avec ses variants en une seule requête. Cette API permet de créer un produit et tous ses variants (couleurs, tailles, etc.) en une seule opération atomique.

## Authentification
- **Type** : Token Authentication
- **Header** : `Authorization: Token <your_token>`
- **Permission requise** : `inventory_create`

## Corps de la requête

### Champs du produit

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `name` | string | Oui | Nom du produit (max 200 caractères) |
| `description` | string | Non | Description détaillée du produit |
| `short_description` | string | Non | Description courte (max 500 caractères) |
| `sku` | string | Oui | Code SKU unique du produit (max 100 caractères) |
| `barcode` | string | Non | Code-barres du produit (max 100 caractères) |
| `category` | integer | Oui | ID de la catégorie du produit |
| `product_type` | string | Non | Type de produit (`simple`, `variable`, `bundle`) - défaut: `simple` |
| `status` | string | Non | Statut du produit (`active`, `inactive`, `discontinued`, `out_of_stock`) - défaut: `active` |
| `price` | decimal | Oui | Prix de base du produit (max 10 chiffres, 2 décimales) |
| `cost_price` | decimal | Non | Prix de revient du produit (max 10 chiffres, 2 décimales) |
| `weight` | decimal | Non | Poids du produit (max 8 chiffres, 2 décimales) |
| `dimensions` | string | Non | Dimensions du produit (max 100 caractères) |
| `is_digital` | boolean | Non | Indique si le produit est numérique - défaut: `false` |
| `is_featured` | boolean | Non | Indique si le produit est mis en avant - défaut: `false` |
| `tags` | string | Non | Tags séparés par des virgules (max 500 caractères) |
| `meta_title` | string | Non | Titre SEO (max 200 caractères) |
| `meta_description` | string | Non | Description SEO (max 500 caractères) |
| `variants` | array | Non | Liste des variants du produit |

### Champs des variants

| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `name` | string | Oui | Nom du variant (ex: "Rouge - Taille S") |
| `sku` | string | Oui | Code SKU unique du variant |
| `variant_type` | string | Oui | Type de variant (`size`, `color`, `material`, `style`, `other`) |
| `value` | string | Oui | Valeur du variant (ex: "Rouge", "L", "Cuir") |
| `price_modifier` | decimal | Non | Modification du prix par rapport au produit de base - défaut: `0.00` |
| `stock_quantity` | integer | Non | Quantité en stock - défaut: `0` |
| `min_stock_level` | integer | Non | Niveau de stock minimum - défaut: `0` |
| `max_stock_level` | integer | Non | Niveau de stock maximum - défaut: `1000` |
| `is_active` | boolean | Non | Indique si le variant est actif - défaut: `true` |
| `sort_order` | integer | Non | Ordre d'affichage - défaut: ordre de création |
| `images` | array | Non | Liste des images spécifiques au variant (optionnel) |

## Exemple de requête

```json
{
  "name": "T-shirt Premium",
  "description": "T-shirt premium en coton bio de qualité supérieure",
  "short_description": "T-shirt confortable et élégant",
  "sku": "TSH-PREMIUM-001",
  "category": 1,
  "product_type": "variable",
  "status": "active",
  "price": 35.00,
  "cost_price": 20.00,
  "is_featured": true,
  "tags": "t-shirt, premium, coton, bio",
  "variants": [
    {
      "name": "Rouge - Taille S",
      "sku": "TSH-PREMIUM-RED-S",
      "variant_type": "color",
      "value": "Rouge",
      "price_modifier": 0.00,
      "stock_quantity": 25,
      "min_stock_level": 5,
      "max_stock_level": 100
    },
    {
      "name": "Rouge - Taille M",
      "sku": "TSH-PREMIUM-RED-M",
      "variant_type": "color",
      "value": "Rouge",
      "price_modifier": 0.00,
      "stock_quantity": 30,
      "min_stock_level": 5,
      "max_stock_level": 100
    },
    {
      "name": "Bleu - Taille S",
      "sku": "TSH-PREMIUM-BLUE-S",
      "variant_type": "color",
      "value": "Bleu",
      "price_modifier": 2.00,
      "stock_quantity": 20,
      "min_stock_level": 5,
      "max_stock_level": 100
    },
    {
      "name": "Bleu - Taille M",
      "sku": "TSH-PREMIUM-BLUE-M",
      "variant_type": "color",
      "value": "Bleu",
      "price_modifier": 2.00,
      "stock_quantity": 25,
      "min_stock_level": 5,
      "max_stock_level": 100,
      "images": [
        {
          "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
          "alt_text": "T-shirt bleu taille M vue de face",
          "is_primary": true,
          "sort_order": 1
        },
        {
          "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
          "alt_text": "T-shirt bleu taille M vue de dos",
          "is_primary": false,
          "sort_order": 2
        }
      ]
    }
  ]
}
```

## Réponses

### Succès (201 Created)
```json
{
  "id": 5,
  "name": "T-shirt Premium",
  "description": "T-shirt premium en coton bio de qualité supérieure",
  "short_description": "T-shirt confortable et élégant",
  "sku": "TSH-PREMIUM-001",
  "barcode": null,
  "category": 1,
  "category_name": "Catégorie 1",
  "product_type": "variable",
  "status": "active",
  "price": "35.00",
  "cost_price": "20.00",
  "weight": null,
  "dimensions": null,
  "is_digital": false,
  "is_featured": true,
  "tags": "t-shirt, premium, coton, bio",
  "tag_list": ["t-shirt", "premium", "coton", "bio"],
  "meta_title": null,
  "meta_description": null,
  "total_stock": 100,
  "variants": [
    {
      "id": 3,
      "name": "Rouge - Taille S",
      "sku": "TSH-PREMIUM-RED-S",
      "variant_type": "color",
      "value": "Rouge",
      "price_modifier": "0.00",
      "final_price": 35.0,
      "stock_quantity": 25,
      "min_stock_level": 5,
      "max_stock_level": 100,
      "is_active": true,
      "sort_order": 1,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-10T12:45:00.000000+02:00",
      "updated_at": "2025-10-10T12:45:00.000000+02:00"
    },
    {
      "id": 4,
      "name": "Rouge - Taille M",
      "sku": "TSH-PREMIUM-RED-M",
      "variant_type": "color",
      "value": "Rouge",
      "price_modifier": "0.00",
      "final_price": 35.0,
      "stock_quantity": 30,
      "min_stock_level": 5,
      "max_stock_level": 100,
      "is_active": true,
      "sort_order": 2,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-10T12:45:00.000000+02:00",
      "updated_at": "2025-10-10T12:45:00.000000+02:00"
    },
    {
      "id": 5,
      "name": "Bleu - Taille S",
      "sku": "TSH-PREMIUM-BLUE-S",
      "variant_type": "color",
      "value": "Bleu",
      "price_modifier": "2.00",
      "final_price": 37.0,
      "stock_quantity": 20,
      "min_stock_level": 5,
      "max_stock_level": 100,
      "is_active": true,
      "sort_order": 3,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-10T12:45:00.000000+02:00",
      "updated_at": "2025-10-10T12:45:00.000000+02:00"
    },
    {
      "id": 6,
      "name": "Bleu - Taille M",
      "sku": "TSH-PREMIUM-BLUE-M",
      "variant_type": "color",
      "value": "Bleu",
      "price_modifier": "2.00",
      "final_price": 37.0,
      "stock_quantity": 25,
      "min_stock_level": 5,
      "max_stock_level": 100,
      "is_active": true,
      "sort_order": 4,
      "is_low_stock": false,
      "is_out_of_stock": false,
      "created_at": "2025-10-10T12:45:00.000000+02:00",
      "updated_at": "2025-10-10T12:45:00.000000+02:00"
    }
  ],
  "images": [],
  "created_at": "2025-10-10T12:45:00.000000+02:00",
  "updated_at": "2025-10-10T12:45:00.000000+02:00"
}
```

### Erreur - Permission refusée (403 Forbidden)
```json
{
  "error": "Permission refusée",
  "detail": "Vous n'avez pas la permission de créer des produits",
  "required_permission": "inventory_create"
}
```

### Erreur - Validation (400 Bad Request)
```json
{
  "name": ["Ce champ est obligatoire."],
  "sku": ["Un produit avec ce SKU existe déjà."],
  "variants": [
    "Le variant 1 doit avoir le champ 'name'"
  ]
}
```

### Erreur - Profil utilisateur non trouvé (400 Bad Request)
```json
{
  "error": "Profil utilisateur non trouvé",
  "detail": "Vous devez être associé à une entreprise pour créer des produits"
}
```

## Comportement spécial

### Association automatique à l'entreprise
- Le produit créé est **automatiquement associé** à l'entreprise de l'utilisateur connecté
- Tous les variants sont également associés à la même entreprise
- L'utilisateur ne peut créer des produits que pour sa propre entreprise

### Validation des SKU
- Le SKU du produit doit être unique dans le système
- Chaque SKU de variant doit être unique dans le système
- Si un SKU existe déjà, une erreur de validation est retournée

### Gestion des variants
- Les variants sont créés **atomiquement** avec le produit
- Si la création d'un variant échoue, toute l'opération est annulée
- Les variants sont automatiquement triés par ordre de création

### Calcul du stock total
- Le `total_stock` du produit est automatiquement calculé comme la somme des stocks de tous ses variants
- Les variants inactifs ne sont pas comptés dans le stock total

## Exemples d'utilisation

### Exemple 1 : Produit simple sans variants
```bash
curl -X POST "http://localhost:8000/api/inventory/products/with-variants/" \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Café Premium",
    "description": "Café en grains de qualité supérieure",
    "sku": "CAFE-PREMIUM-001",
    "category": 2,
    "product_type": "simple",
    "price": 15.50,
    "cost_price": 10.00
  }'
```

### Exemple 2 : Produit avec variants de taille
```bash
curl -X POST "http://localhost:8000/api/inventory/products/with-variants/" \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Chaussures Sport",
    "sku": "SHOES-SPORT-001",
    "category": 3,
    "product_type": "variable",
    "price": 89.99,
    "variants": [
      {
        "name": "Noir - Taille 40",
        "sku": "SHOES-SPORT-BLACK-40",
        "variant_type": "size",
        "value": "40",
        "stock_quantity": 15
      },
      {
        "name": "Noir - Taille 41",
        "sku": "SHOES-SPORT-BLACK-41",
        "variant_type": "size",
        "value": "41",
        "stock_quantity": 20
      }
    ]
  }'
```

### Exemple 3 : Produit avec variants de couleur et taille
```bash
curl -X POST "http://localhost:8000/api/inventory/products/with-variants/" \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sac à dos",
    "sku": "BAG-BACKPACK-001",
    "category": 4,
    "product_type": "variable",
    "price": 45.00,
    "variants": [
      {
        "name": "Noir - 20L",
        "sku": "BAG-BACKPACK-BLACK-20L",
        "variant_type": "color",
        "value": "Noir",
        "price_modifier": 0.00,
        "stock_quantity": 10
      },
      {
        "name": "Bleu - 20L",
        "sku": "BAG-BACKPACK-BLUE-20L",
        "variant_type": "color",
        "value": "Bleu",
        "price_modifier": 5.00,
        "stock_quantity": 8
      },
      {
        "name": "Noir - 30L",
        "sku": "BAG-BACKPACK-BLACK-30L",
        "variant_type": "size",
        "value": "30L",
        "price_modifier": 10.00,
        "stock_quantity": 12
      }
    ]
  }'
```

## Gestion des images

### Images liées aux variants
- Chaque variant peut avoir ses propres images (optionnel)
- Les images sont spécifiques à la couleur/taille du variant
- Une image peut être liée soit à un produit soit à un variant (pas les deux)
- Si un variant n'a pas d'images, il hérite des images du produit parent
- Les images de variants sont prioritaires sur les images du produit

### Structure des images dans la réponse
```json
{
  "images": [
    {
      "id": 1,
      "image": "http://localhost:8000/media/products/tshirt-rouge-1.jpg",
      "alt_text": "T-shirt rouge vue de face",
      "is_primary": true,
      "sort_order": 1
    },
    {
      "id": 2,
      "image": "http://localhost:8000/media/products/tshirt-rouge-2.jpg",
      "alt_text": "T-shirt rouge vue de dos",
      "is_primary": false,
      "sort_order": 2
    }
  ]
}
```

## Notes importantes

1. **Opération atomique** : Si la création d'un variant échoue, tout le produit et ses variants sont supprimés
2. **Filtrage par entreprise** : Seuls les produits de l'entreprise de l'utilisateur sont visibles
3. **Validation stricte** : Tous les champs requis doivent être fournis
4. **SKU uniques** : Les SKU doivent être uniques à la fois pour les produits et les variants
5. **Types de variants** : Utilisez les types prédéfinis (`size`, `color`, `material`, `style`, `other`)
6. **Images spécifiques** : Chaque variant peut avoir ses propres images pour une meilleure expérience utilisateur

## Codes de statut HTTP

- `201 Created` : Produit et variants créés avec succès
- `400 Bad Request` : Erreur de validation ou données manquantes
- `403 Forbidden` : Permission insuffisante
- `500 Internal Server Error` : Erreur serveur
