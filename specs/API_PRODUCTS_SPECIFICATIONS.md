# 📦 API Specifications - Products & Inventory Management
## Baobab ERP System

This document provides comprehensive specifications for all product and inventory management APIs in the Baobab ERP system.

---

## 🌐 Base URL
```
http://localhost:8000/api/inventory/
```
**Production:** `https://your-domain.com/api/inventory/`

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
    "username": "your_username",
    "password": "your_password"
}
```

---

## 📋 Table of Contents
1. [Categories Management](#categories-management)
2. [Products Management](#products-management)
3. [Product Variants Management](#product-variants-management)
4. [Product Images Management](#product-images-management)
5. [Search & Filtering](#search--filtering)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)

---

## 🏷️ Categories Management

### 1. List Categories
**Endpoint:** `GET /api/inventory/categories/`

**Description:** Retrieve all categories with optional filtering and pagination.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `is_active` (boolean): Filter by active status
- `parent` (int): Filter by parent category ID
- `search` (string): Search in name and description
- `ordering` (string): Order by field (name, sort_order, created_at)

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/inventory/categories/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Électronique",
            "description": "Appareils électroniques et accessoires",
            "parent": null,
            "image": "http://localhost:8000/media/categories/electronics.jpg",
            "is_active": true,
            "sort_order": 1,
            "full_name": "Électronique",
            "children_count": 3,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        },
        {
            "id": 2,
            "name": "Smartphones",
            "description": "Téléphones intelligents",
            "parent": 1,
            "image": "http://localhost:8000/media/categories/smartphones.jpg",
            "is_active": true,
            "sort_order": 1,
            "full_name": "Électronique > Smartphones",
            "children_count": 0,
            "created_at": "2024-01-15T10:35:00Z",
            "updated_at": "2024-01-15T10:35:00Z"
        }
    ]
}
```

### 2. Get Category Details
**Endpoint:** `GET /api/inventory/categories/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Électronique",
    "description": "Appareils électroniques et accessoires",
    "parent": null,
    "image": "http://localhost:8000/media/categories/electronics.jpg",
    "is_active": true,
    "sort_order": 1,
    "full_name": "Électronique",
    "children_count": 3,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Category
**Endpoint:** `POST /api/inventory/categories/`

**Required Permission:** `inventory_category.create`

**Request Body:**
```json
{
    "name": "Nouvelle Catégorie",
    "description": "Description de la nouvelle catégorie",
    "parent": 1,
    "image": "base64_encoded_image_or_file_upload",
    "is_active": true,
    "sort_order": 5
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "name": "Nouvelle Catégorie",
    "description": "Description de la nouvelle catégorie",
    "parent": 1,
    "image": "http://localhost:8000/media/categories/new_category.jpg",
    "is_active": true,
    "sort_order": 5,
    "full_name": "Électronique > Nouvelle Catégorie",
    "children_count": 0,
    "created_at": "2024-01-15T11:00:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
}
```

### 4. Update Category
**Endpoint:** `PUT /api/inventory/categories/{id}/` or `PATCH /api/inventory/categories/{id}/`

**Required Permission:** `inventory_category.update`

**Request Body (PUT - Complete Update):**
```json
{
    "name": "Catégorie Modifiée",
    "description": "Description mise à jour",
    "parent": 1,
    "is_active": true,
    "sort_order": 3
}
```

**Response (200 OK):** Same as Get Category Details

### 5. Delete Category
**Endpoint:** `DELETE /api/inventory/categories/{id}/`

**Required Permission:** `inventory_category.delete`

**Response (204 No Content):** Empty response body

### 6. Get Active Categories
**Endpoint:** `GET /api/inventory/categories/active/`

**Description:** Returns only active categories.

**Response (200 OK):** Same structure as List Categories, but only active categories.

### 7. Get Category Products
**Endpoint:** `GET /api/inventory/categories/{id}/products/`

**Description:** Returns all products in this category.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "iPhone 15",
        "sku": "IPH15-001",
        "category": 2,
        "category_name": "Smartphones",
        "product_type": "simple",
        "status": "active",
        "price": "999.99",
        "is_featured": true,
        "total_stock": 50,
        "primary_image": {
            "id": 1,
            "image": "http://localhost:8000/media/products/iphone15.jpg",
            "alt_text": "iPhone 15"
        },
        "created_at": "2024-01-15T12:00:00Z"
    }
]
```

---

## 📦 Products Management

### 1. List Products
**Endpoint:** `GET /api/inventory/products/`

**Description:** Retrieve all products with optional filtering and pagination.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `status` (string): Filter by status (active, inactive, discontinued, out_of_stock)
- `product_type` (string): Filter by type (simple, variable, bundle)
- `category` (int): Filter by category ID
- `is_digital` (boolean): Filter digital products
- `is_featured` (boolean): Filter featured products
- `search` (string): Search in name, description, SKU, barcode, tags
- `ordering` (string): Order by field (name, price, created_at, updated_at)

**Response (200 OK):**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/inventory/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "iPhone 15",
            "sku": "IPH15-001",
            "category": 2,
            "category_name": "Smartphones",
            "product_type": "simple",
            "status": "active",
            "price": "999.99",
            "is_featured": true,
            "total_stock": 50,
            "primary_image": {
                "id": 1,
                "image": "http://localhost:8000/media/products/iphone15.jpg",
                "alt_text": "iPhone 15"
            },
            "created_at": "2024-01-15T12:00:00Z"
        }
    ]
}
```

### 2. Get Product Details
**Endpoint:** `GET /api/inventory/products/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "iPhone 15",
    "description": "Le dernier iPhone avec des fonctionnalités avancées",
    "short_description": "iPhone 15 - 128GB",
    "sku": "IPH15-001",
    "barcode": "1234567890123",
    "category": 2,
    "category_name": "Smartphones",
    "product_type": "simple",
    "status": "active",
    "price": "999.99",
    "cost_price": "750.00",
    "weight": "0.174",
    "dimensions": "147.6 x 71.6 x 7.80 mm",
    "is_digital": false,
    "is_featured": true,
    "tags": "smartphone,apple,ios,5g",
    "tag_list": ["smartphone", "apple", "ios", "5g"],
    "meta_title": "iPhone 15 - Acheter maintenant",
    "meta_description": "Découvrez le nouvel iPhone 15 avec des fonctionnalités révolutionnaires",
    "total_stock": 50,
    "variants": [
        {
            "id": 1,
            "name": "128GB - Noir",
            "sku": "IPH15-001-128-BLK",
            "variant_type": "other",
            "value": "128GB - Noir",
            "price_modifier": "0.00",
            "final_price": "999.99",
            "stock_quantity": 25,
            "min_stock_level": 5,
            "max_stock_level": 100,
            "is_active": true,
            "sort_order": 1,
            "is_low_stock": false,
            "is_out_of_stock": false,
            "created_at": "2024-01-15T12:00:00Z",
            "updated_at": "2024-01-15T12:00:00Z"
        }
    ],
    "images": [
        {
            "id": 1,
            "image": "http://localhost:8000/media/products/iphone15.jpg",
            "alt_text": "iPhone 15 - Vue de face",
            "is_primary": true,
            "sort_order": 1,
            "created_at": "2024-01-15T12:00:00Z",
            "updated_at": "2024-01-15T12:00:00Z"
        }
    ],
    "created_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
}
```

### 3. Create Product
**Endpoint:** `POST /api/inventory/products/`

**Required Permission:** `inventory_create`

**Request Body:**
```json
{
    "name": "Samsung Galaxy S24",
    "description": "Le dernier smartphone Samsung avec IA intégrée",
    "short_description": "Galaxy S24 - 256GB",
    "sku": "SGS24-001",
    "barcode": "1234567890124",
    "category": 2,
    "product_type": "variable",
    "status": "active",
    "price": "899.99",
    "cost_price": "650.00",
    "weight": "0.168",
    "dimensions": "147.0 x 70.6 x 7.6 mm",
    "is_digital": false,
    "is_featured": false,
    "tags": "smartphone,samsung,android,5g",
    "meta_title": "Samsung Galaxy S24 - Acheter maintenant",
    "meta_description": "Découvrez le Galaxy S24 avec l'IA Galaxy"
}
```

**Response (201 Created):** Same as Get Product Details

### 4. Update Product
**Endpoint:** `PUT /api/inventory/products/{id}/` or `PATCH /api/inventory/products/{id}/`

**Required Permission:** `inventory_update`

**Request Body (PATCH - Partial Update):**
```json
{
    "price": "949.99",
    "is_featured": true,
    "status": "active",
    "images": [
        {
            "id": 1,
            "alt_text": "Nouvelle description de l'image",
            "is_primary": true,
            "sort_order": 1
        },
        {
            "image": "base64_encoded_image_or_file_upload",
            "alt_text": "Nouvelle image",
            "is_primary": false,
            "sort_order": 2
        }
    ],
    "images_to_delete": [3, 4]
}
```

**Image Management Fields:**
- `images` (array, optional): Array of image objects to update or create
  - `id` (int, optional): Image ID for updates (omit for new images)
  - `image` (file/string, optional): Image file or base64 data (for new images)
  - `alt_text` (string, optional): Alternative text for accessibility
  - `is_primary` (boolean, optional): Whether this is the primary image
  - `sort_order` (int, optional): Display order (0 = first)
- `images_to_delete` (array, optional): Array of image IDs to delete

**Response (200 OK):** Same as Get Product Details

**Image Management Examples:**

**Add new images:**
```json
{
    "images": [
        {
            "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "alt_text": "Vue de face du produit",
            "is_primary": true,
            "sort_order": 1
        }
    ]
}
```

**Update existing images:**
```json
{
    "images": [
        {
            "id": 1,
            "alt_text": "Description mise à jour",
            "is_primary": false,
            "sort_order": 2
        }
    ]
}
```

**Delete images:**
```json
{
    "images_to_delete": [2, 3]
}
```

**Mixed operations (update, add, delete):**
```json
{
    "images": [
        {
            "id": 1,
            "alt_text": "Image principale mise à jour",
            "is_primary": true,
            "sort_order": 1
        },
        {
            "image": "new_image_file.jpg",
            "alt_text": "Nouvelle image",
            "is_primary": false,
            "sort_order": 3
        }
    ],
    "images_to_delete": [2, 4]
}
```

### 5. Delete Product
**Endpoint:** `DELETE /api/inventory/products/{id}/`

**Required Permission:** `inventory_delete`

**Response (204 No Content):** Empty response body

### 6. Get Active Products
**Endpoint:** `GET /api/inventory/products/active/`

**Description:** Returns only active products.

**Response (200 OK):** Same structure as List Products, but only active products.

### 7. Get Featured Products
**Endpoint:** `GET /api/inventory/products/featured/`

**Description:** Returns only featured products.

**Response (200 OK):** Same structure as List Products, but only featured products.

### 8. Get Product Variants
**Endpoint:** `GET /api/inventory/products/{id}/variants/`

**Description:** Returns all variants of a specific product.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "name": "128GB - Noir",
        "sku": "IPH15-001-128-BLK",
        "variant_type": "other",
        "value": "128GB - Noir",
        "price_modifier": "0.00",
        "final_price": "999.99",
        "stock_quantity": 25,
        "min_stock_level": 5,
        "max_stock_level": 100,
        "is_active": true,
        "sort_order": 1,
        "is_low_stock": false,
        "is_out_of_stock": false,
        "created_at": "2024-01-15T12:00:00Z",
        "updated_at": "2024-01-15T12:00:00Z"
    }
]
```

### 9. Search Products
**Endpoint:** `GET /api/inventory/products/search/?q={query}`

**Description:** Advanced product search across multiple fields.

**Query Parameters:**
- `q` (string, required): Search query

**Response (200 OK):** Same structure as List Products

---

## 🔧 Product Variants Management

### 1. List Product Variants
**Endpoint:** `GET /api/inventory/variants/`

**Description:** Retrieve all product variants with optional filtering.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `product` (int): Filter by product ID
- `variant_type` (string): Filter by variant type (size, color, material, style, other)
- `is_active` (boolean): Filter by active status
- `search` (string): Search in name, SKU, value
- `ordering` (string): Order by field (name, sort_order, stock_quantity)

**Response (200 OK):**
```json
{
    "count": 75,
    "next": "http://localhost:8000/api/inventory/variants/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "product": 1,
            "name": "128GB - Noir",
            "sku": "IPH15-001-128-BLK",
            "variant_type": "other",
            "value": "128GB - Noir",
            "price_modifier": "0.00",
            "final_price": "999.99",
            "stock_quantity": 25,
            "min_stock_level": 5,
            "max_stock_level": 100,
            "is_active": true,
            "sort_order": 1,
            "is_low_stock": false,
            "is_out_of_stock": false,
            "created_at": "2024-01-15T12:00:00Z",
            "updated_at": "2024-01-15T12:00:00Z"
        }
    ]
}
```

### 2. Get Variant Details
**Endpoint:** `GET /api/inventory/variants/{id}/`

**Response (200 OK):** Same as variant object in List Product Variants

### 3. Create Product Variant
**Endpoint:** `POST /api/inventory/variants/`

**Required Permission:** `inventory_variant.create`

**Request Body:**
```json
{
    "product": 1,
    "name": "256GB - Bleu",
    "sku": "IPH15-001-256-BLU",
    "variant_type": "color",
    "value": "Bleu",
    "price_modifier": "100.00",
    "stock_quantity": 15,
    "min_stock_level": 3,
    "max_stock_level": 50,
    "is_active": true,
    "sort_order": 2
}
```

**Response (201 Created):** Same as Get Variant Details

### 4. Update Product Variant
**Endpoint:** `PUT /api/inventory/variants/{id}/` or `PATCH /api/inventory/variants/{id}/`

**Required Permission:** `inventory_variant.update`

**Request Body (PATCH - Partial Update):**
```json
{
    "stock_quantity": 20,
    "price_modifier": "150.00"
}
```

**Response (200 OK):** Same as Get Variant Details

### 5. Delete Product Variant
**Endpoint:** `DELETE /api/inventory/variants/{id}/`

**Required Permission:** `inventory_variant.delete`

**Response (204 No Content):** Empty response body

---

## 🖼️ Product Images Management

### 1. List Product Images
**Endpoint:** `GET /api/inventory/products/{product_id}/images/`

**Description:** Get all images for a specific product.

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "image": "http://localhost:8000/media/products/iphone15.jpg",
        "alt_text": "iPhone 15 - Vue de face",
        "is_primary": true,
        "sort_order": 1,
        "created_at": "2024-01-15T12:00:00Z",
        "updated_at": "2024-01-15T12:00:00Z"
    },
    {
        "id": 2,
        "image": "http://localhost:8000/media/products/iphone15_back.jpg",
        "alt_text": "iPhone 15 - Vue arrière",
        "is_primary": false,
        "sort_order": 2,
        "created_at": "2024-01-15T12:05:00Z",
        "updated_at": "2024-01-15T12:05:00Z"
    }
]
```

### 2. Integrated Image Management
**Endpoint:** `PATCH /api/inventory/products/{id}/`

**Description:** Manage product images directly through the product update endpoint. This is the recommended approach for image management.

**Required Permission:** `inventory_update`

**Image Operations:**

#### Add New Images
```json
{
    "images": [
        {
            "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "alt_text": "Vue de face du produit",
            "is_primary": true,
            "sort_order": 1
        },
        {
            "image": "new_image_file.jpg",
            "alt_text": "Vue de côté",
            "is_primary": false,
            "sort_order": 2
        }
    ]
}
```

#### Update Existing Images
```json
{
    "images": [
        {
            "id": 1,
            "alt_text": "Description mise à jour",
            "is_primary": false,
            "sort_order": 3
        },
        {
            "id": 2,
            "is_primary": true,
            "sort_order": 1
        }
    ]
}
```

#### Delete Images
```json
{
    "images_to_delete": [3, 4, 5]
}
```

#### Mixed Operations (Recommended)
```json
{
    "name": "iPhone 15 Pro",
    "price": "1099.99",
    "images": [
        {
            "id": 1,
            "alt_text": "Image principale mise à jour",
            "is_primary": true,
            "sort_order": 1
        },
        {
            "image": "new_side_view.jpg",
            "alt_text": "Nouvelle vue de côté",
            "is_primary": false,
            "sort_order": 2
        }
    ],
    "images_to_delete": [2, 3]
}
```

**Image Field Specifications:**
- `id` (int, optional): Image ID for updates (omit for new images)
- `image` (file/string, required for new images): Image file or base64 data
- `alt_text` (string, optional): Alternative text for accessibility (max 200 chars)
- `is_primary` (boolean, optional): Whether this is the primary image (only one per product)
- `sort_order` (int, optional): Display order (0 = first, higher numbers = later)

**Validation Rules:**
- Only one image can be marked as primary per product
- If no image is marked as primary, the first image becomes primary automatically
- Image files must be valid image formats (JPEG, PNG, GIF, WebP)
- Maximum file size: 10MB per image
- Maximum 10 images per product

**Response (200 OK):** Updated product with all images included

---

## 🔍 Search & Filtering

### Advanced Search Parameters

**Categories:**
- `search`: Search in name and description
- `is_active`: Filter by active status
- `parent`: Filter by parent category

**Products:**
- `search`: Search in name, description, SKU, barcode, tags
- `status`: Filter by product status
- `product_type`: Filter by product type
- `category`: Filter by category
- `is_digital`: Filter digital products
- `is_featured`: Filter featured products

**Variants:**
- `search`: Search in name, SKU, value
- `product`: Filter by product
- `variant_type`: Filter by variant type
- `is_active`: Filter by active status

### Ordering Options

**Categories:** `name`, `sort_order`, `created_at`
**Products:** `name`, `price`, `created_at`, `updated_at`
**Variants:** `name`, `sort_order`, `stock_quantity`

### Pagination

All list endpoints support pagination:
- `page`: Page number (starts from 1)
- `limit`: Items per page (default: 20, max: 100)

---

## ❌ Error Handling

### Common Error Responses

**400 Bad Request:**
```json
{
    "error": "Validation Error",
    "details": {
        "name": ["This field is required."],
        "sku": ["A product with this SKU already exists."]
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
    "detail": "Vous n'avez pas la permission de voir les produits",
    "required_permission": "inventory_view"
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

### Product Status Values
- `active`: Actif
- `inactive`: Inactif
- `discontinued`: Discontinué
- `out_of_stock`: Rupture de stock

### Product Type Values
- `simple`: Produit simple
- `variable`: Produit avec variants
- `bundle`: Pack/Lot

### Variant Type Values
- `size`: Taille
- `color`: Couleur
- `material`: Matière
- `style`: Style
- `other`: Autre

### Field Validations

**Product:**
- `name`: Required, max 200 characters
- `sku`: Required, unique, max 100 characters
- `barcode`: Optional, unique, max 100 characters
- `price`: Required, min 0.01
- `cost_price`: Optional, min 0.00

**ProductVariant:**
- `name`: Required, max 100 characters
- `sku`: Required, unique, max 100 characters
- `stock_quantity`: Default 0, min 0
- `min_stock_level`: Default 0, min 0
- `max_stock_level`: Default 1000, min 0

**Category:**
- `name`: Required, unique, max 100 characters
- `sort_order`: Default 0, min 0

---

## 🚀 Usage Examples

### JavaScript/Fetch Examples

**Get all products:**
```javascript
const response = await fetch('/api/inventory/products/', {
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```

**Create a new product:**
```javascript
const response = await fetch('/api/inventory/products/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: 'New Product',
        sku: 'NEW-001',
        category: 1,
        product_type: 'simple',
        status: 'active',
        price: '99.99',
        cost_price: '50.00'
    })
});
const product = await response.json();
```

**Update a product:**
```javascript
const response = await fetch('/api/inventory/products/1/', {
    method: 'PATCH',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        price: '949.99',
        is_featured: true,
        status: 'active'
    })
});
const product = await response.json();
```

**Update product with images:**
```javascript
const response = await fetch('/api/inventory/products/1/', {
    method: 'PATCH',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: 'iPhone 15 Pro',
        price: '1099.99',
        images: [
            {
                id: 1,
                alt_text: 'Image principale mise à jour',
                is_primary: true,
                sort_order: 1
            },
            {
                image: 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...',
                alt_text: 'Nouvelle vue de côté',
                is_primary: false,
                sort_order: 2
            }
        ],
        images_to_delete: [2, 3]
    })
});
const product = await response.json();
```

**Search products:**
```javascript
const response = await fetch('/api/inventory/products/search/?q=iphone', {
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const results = await response.json();
```

### cURL Examples

**Get product details:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/inventory/products/1/
```

**Update a product with images:**
```bash
curl -X PATCH \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "iPhone 15 Pro",
       "price": "1099.99",
       "images": [
         {
           "id": 1,
           "alt_text": "Image principale mise à jour",
           "is_primary": true,
           "sort_order": 1
         },
         {
           "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
           "alt_text": "Nouvelle vue de côté",
           "is_primary": false,
           "sort_order": 2
         }
       ],
       "images_to_delete": [2, 3]
     }' \
     http://localhost:8000/api/inventory/products/1/
```

**Create a category:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"name": "New Category", "description": "Category description"}' \
     http://localhost:8000/api/inventory/categories/
```

---

## 📝 Notes

1. **File Uploads**: For image uploads, use `multipart/form-data` content type
2. **Pagination**: All list endpoints return paginated results
3. **Permissions**: Each endpoint requires specific permissions
4. **Search**: Search is case-insensitive and works across multiple fields
5. **Validation**: All fields are validated according to model constraints
6. **Timestamps**: All timestamps are in ISO 8601 format (UTC)

---

**🎉 Your Product APIs are ready for integration!**

This comprehensive API specification covers all product and inventory management functionality in the Baobab ERP system. The APIs are fully secured with authentication and permission-based access control.
