# 💰 API Specifications - Sales Management
## Baobab ERP System

This document provides comprehensive specifications for all sales management APIs in the Baobab ERP system.

---

## 🌐 Base URL
```
http://localhost:8000/api/sales/
```
**Production:** `https://your-domain.com/api/sales/`

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
1. [Orders Management](#orders-management)
2. [Order Items Management](#order-items-management)
3. [Invoices Management](#invoices-management)
4. [Proforma Invoices Management](#proforma-invoices-management)
5. [Payments Management](#payments-management)
6. [Sales Analytics](#sales-analytics)
7. [Error Handling](#error-handling)
8. [Data Models](#data-models)

---

## 📦 Orders Management

### 1. List Orders
**Endpoint:** `GET /api/sales/orders/`

**Description:** Retrieve all orders with optional filtering and pagination.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `customer` (int): Filter by customer ID
- `status` (string): Filter by order status
- `user` (int): Filter by user ID
- `date_from` (date): Filter orders from date (YYYY-MM-DD)
- `date_to` (date): Filter orders to date (YYYY-MM-DD)
- `search` (string): Search in order number, customer name, notes
- `ordering` (string): Order by field (created_at, order_date, total_amount)

**Response (200 OK):**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/sales/orders/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "customer_name": "Jean Dupont",
            "order_number": "ORD-2024-001",
            "status": "confirmed",
            "order_date": "2024-01-15T10:30:00Z",
            "total_amount": "1250.50",
            "user_name": "Admin User",
            "items_count": 3,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Order Details
**Endpoint:** `GET /api/sales/orders/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "customer": 1,
    "customer_name": "Jean Dupont",
    "order_number": "ORD-2024-001",
    "status": "confirmed",
    "order_date": "2024-01-15T10:30:00Z",
    "delivery_date": "2024-01-20T00:00:00Z",
    "subtotal": "1042.08",
    "tax_rate": "20.00",
    "tax_amount": "208.42",
    "total_amount": "1250.50",
    "discount_rate": "0.00",
    "discount_amount": "0.00",
    "notes": "Livraison urgente",
    "internal_notes": "Client VIP",
    "user": 1,
    "user_name": "Admin User",
    "items": [
        {
            "id": 1,
            "order": 1,
            "product": 1,
            "variant": 1,
            "quantity": 2,
            "unit_price": "500.00",
            "discount_rate": "0.00",
            "discount_amount": "0.00",
            "total_price": "1000.00",
            "product_name": "iPhone 15",
            "final_unit_price": "500.00",
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-15T10:30:00Z"
        }
    ],
    "is_pending": false,
    "is_confirmed": true,
    "is_shipped": false,
    "is_delivered": false,
    "is_cancelled": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Order
**Endpoint:** `POST /api/sales/orders/`

**Required Permission:** `sales_orders_create`

**Request Body:**
```json
{
    "customer": 1,
    "status": "pending",
    "order_date": "2024-01-15T10:30:00Z",
    "delivery_date": "2024-01-20T00:00:00Z",
    "tax_rate": "20.00",
    "discount_rate": "5.00",
    "notes": "Commande urgente",
    "internal_notes": "Client VIP",
    "items": [
        {
            "product": 1,
            "variant": 1,
            "quantity": 2,
            "unit_price": "500.00",
            "discount_rate": "0.00"
        },
        {
            "product": 2,
            "quantity": 1,
            "unit_price": "250.00",
            "discount_rate": "10.00"
        }
    ]
}
```

**Response (201 Created):** Same as Get Order Details

### 4. Update Order
**Endpoint:** `PUT /api/sales/orders/{id}/` or `PATCH /api/sales/orders/{id}/`

**Required Permission:** `sales_orders_create`

**Request Body (PATCH - Partial Update):**
```json
{
    "status": "confirmed",
    "delivery_date": "2024-01-22T00:00:00Z",
    "notes": "Commande confirmée"
}
```

**Response (200 OK):** Same as Get Order Details

### 5. Delete Order
**Endpoint:** `DELETE /api/sales/orders/{id}/`

**Required Permission:** `sales_orders_create`

**Response (204 No Content):** Empty response body

### 6. Order Status Management

#### Confirm Order
**Endpoint:** `POST /api/sales/orders/{id}/confirm/`

**Required Permission:** `sales_orders_create`

**Response (200 OK):** Updated order details

#### Ship Order
**Endpoint:** `POST /api/sales/orders/{id}/ship/`

**Required Permission:** `sales_orders_create`

**Response (200 OK):** Updated order details

#### Deliver Order
**Endpoint:** `POST /api/sales/orders/{id}/deliver/`

**Required Permission:** `sales_orders_create`

**Response (200 OK):** Updated order details

#### Cancel Order
**Endpoint:** `POST /api/sales/orders/{id}/cancel/`

**Required Permission:** `sales_orders_create`

**Response (200 OK):** Updated order details

### 7. Order Filtering by Status

#### Pending Orders
**Endpoint:** `GET /api/sales/orders/pending/`

**Response (200 OK):** List of pending orders

#### Confirmed Orders
**Endpoint:** `GET /api/sales/orders/confirmed/`

**Response (200 OK):** List of confirmed orders

#### Shipped Orders
**Endpoint:** `GET /api/sales/orders/shipped/`

**Response (200 OK):** List of shipped orders

#### Delivered Orders
**Endpoint:** `GET /api/sales/orders/delivered/`

**Response (200 OK):** List of delivered orders

#### Cancelled Orders
**Endpoint:** `GET /api/sales/orders/cancelled/`

**Response (200 OK):** List of cancelled orders

### 8. Orders Summary
**Endpoint:** `GET /api/sales/orders/summary/`

**Description:** Get comprehensive order statistics.

**Response (200 OK):**
```json
{
    "total_orders": 150,
    "pending_orders": 12,
    "confirmed_orders": 45,
    "shipped_orders": 38,
    "delivered_orders": 55,
    "cancelled_orders": 0,
    "total_revenue": 125000.50,
    "by_status": [
        {"status": "delivered", "count": 55},
        {"status": "confirmed", "count": 45},
        {"status": "shipped", "count": 38},
        {"status": "pending", "count": 12}
    ]
}
```

---

## 🛒 Order Items Management

### 1. List Order Items
**Endpoint:** `GET /api/sales/order-items/`

**Description:** Retrieve all order items with optional filtering.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `order` (int): Filter by order ID
- `product` (int): Filter by product ID
- `variant` (int): Filter by variant ID
- `search` (string): Search in product name, variant name
- `ordering` (string): Order by field (created_at, quantity, unit_price, total_price)

**Response (200 OK):**
```json
{
    "count": 75,
    "next": "http://localhost:8000/api/sales/order-items/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "order_number": "ORD-2024-001",
            "product_name": "iPhone 15",
            "quantity": 2,
            "unit_price": "500.00",
            "total_price": "1000.00",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Order Item Details
**Endpoint:** `GET /api/sales/order-items/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "order": 1,
    "product": 1,
    "variant": 1,
    "quantity": 2,
    "unit_price": "500.00",
    "discount_rate": "0.00",
    "discount_amount": "0.00",
    "total_price": "1000.00",
    "product_name": "iPhone 15",
    "final_unit_price": "500.00",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Order Item
**Endpoint:** `POST /api/sales/order-items/`

**Required Permission:** `sales_orders_create`

**Request Body:**
```json
{
    "order": 1,
    "product": 1,
    "variant": 1,
    "quantity": 2,
    "unit_price": "500.00",
    "discount_rate": "5.00"
}
```

**Response (201 Created):** Same as Get Order Item Details

### 4. Update Order Item
**Endpoint:** `PUT /api/sales/order-items/{id}/` or `PATCH /api/sales/order-items/{id}/`

**Required Permission:** `sales_orders_create`

**Request Body (PATCH - Partial Update):**
```json
{
    "quantity": 3,
    "unit_price": "480.00"
}
```

**Response (200 OK):** Same as Get Order Item Details

### 5. Delete Order Item
**Endpoint:** `DELETE /api/sales/order-items/{id}/`

**Required Permission:** `sales_orders_create`

**Response (204 No Content):** Empty response body

---

## 🧾 Invoices Management

### 1. List Invoices
**Endpoint:** `GET /api/sales/invoices/`

**Description:** Retrieve all invoices with optional filtering and pagination.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `status` (string): Filter by invoice status
- `user` (int): Filter by user ID
- `date_from` (date): Filter invoices from date (YYYY-MM-DD)
- `date_to` (date): Filter invoices to date (YYYY-MM-DD)
- `search` (string): Search in invoice number, customer name
- `ordering` (string): Order by field (created_at, invoice_date, due_date, total_amount)

**Response (200 OK):**
```json
{
    "count": 120,
    "next": "http://localhost:8000/api/sales/invoices/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "invoice_number": "INV-2024-001",
            "customer_name": "Jean Dupont",
            "order_number": "ORD-2024-001",
            "status": "paid",
            "invoice_date": "2024-01-15T10:30:00Z",
            "due_date": "2024-02-15T00:00:00Z",
            "total_amount": "1250.50",
            "paid_amount": "1250.50",
            "remaining_amount": "0.00",
            "is_overdue": false,
            "payment_percentage": 100.0,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Invoice Details
**Endpoint:** `GET /api/sales/invoices/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "order": 1,
    "order_number": "ORD-2024-001",
    "customer_name": "Jean Dupont",
    "invoice_number": "INV-2024-001",
    "status": "paid",
    "invoice_date": "2024-01-15T10:30:00Z",
    "due_date": "2024-02-15T00:00:00Z",
    "subtotal": "1042.08",
    "tax_rate": "20.00",
    "tax_amount": "208.42",
    "total_amount": "1250.50",
    "paid_amount": "1250.50",
    "remaining_amount": "0.00",
    "notes": "Facture pour commande urgente",
    "user": 1,
    "user_name": "Admin User",
    "is_draft": false,
    "is_sent": true,
    "is_paid": true,
    "is_overdue": false,
    "payment_percentage": 100.0,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Invoice
**Endpoint:** `POST /api/sales/invoices/`

**Required Permission:** `sales_invoices_create`

**Request Body:**
```json
{
    "order": 1,
    "status": "draft",
    "invoice_date": "2024-01-15T10:30:00Z",
    "due_date": "2024-02-15T00:00:00Z",
    "notes": "Facture pour commande urgente"
}
```

**Response (201 Created):** Same as Get Invoice Details

### 4. Update Invoice
**Endpoint:** `PUT /api/sales/invoices/{id}/` or `PATCH /api/sales/invoices/{id}/`

**Required Permission:** `sales_invoices_create`

**Request Body (PATCH - Partial Update):**
```json
{
    "status": "sent",
    "notes": "Facture envoyée au client"
}
```

**Response (200 OK):** Same as Get Invoice Details

### 5. Delete Invoice
**Endpoint:** `DELETE /api/sales/invoices/{id}/`

**Required Permission:** `sales_invoices_create`

**Response (204 No Content):** Empty response body

### 6. Invoice Status Management

#### Send Invoice
**Endpoint:** `POST /api/sales/invoices/{id}/send/`

**Required Permission:** `sales_invoices_create`

**Response (200 OK):** Updated invoice details

#### Mark Invoice as Paid
**Endpoint:** `POST /api/sales/invoices/{id}/mark_paid/`

**Required Permission:** `sales_invoices_create`

**Response (200 OK):** Updated invoice details

### 7. Invoice Filtering by Status

#### Draft Invoices
**Endpoint:** `GET /api/sales/invoices/draft/`

**Response (200 OK):** List of draft invoices

#### Sent Invoices
**Endpoint:** `GET /api/sales/invoices/sent/`

**Response (200 OK):** List of sent invoices

#### Paid Invoices
**Endpoint:** `GET /api/sales/invoices/paid/`

**Response (200 OK):** List of paid invoices

#### Overdue Invoices
**Endpoint:** `GET /api/sales/invoices/overdue/`

**Response (200 OK):** List of overdue invoices

### 8. Invoices Summary
**Endpoint:** `GET /api/sales/invoices/summary/`

**Description:** Get comprehensive invoice statistics.

**Response (200 OK):**
```json
{
    "total_invoices": 120,
    "draft_invoices": 5,
    "sent_invoices": 25,
    "paid_invoices": 85,
    "overdue_invoices": 5,
    "total_amount": 150000.00,
    "paid_amount": 125000.00,
    "remaining_amount": 25000.00
}
```

---

## 📋 Proforma Invoices Management

### 1. List Proforma Invoices
**Endpoint:** `GET /api/sales/proformas/`

**Description:** Retrieve all proforma invoices (quotes) with optional filtering.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `customer` (int): Filter by customer ID
- `status` (string): Filter by proforma status
- `user` (int): Filter by user ID
- `date_from` (date): Filter proformas from date (YYYY-MM-DD)
- `date_to` (date): Filter proformas to date (YYYY-MM-DD)
- `search` (string): Search in proforma number, customer name
- `ordering` (string): Order by field (created_at, proforma_date, valid_until, total_amount)

**Response (200 OK):**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/sales/proformas/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "proforma_number": "PRO-2024-001",
            "customer_name": "Jean Dupont",
            "status": "sent",
            "proforma_date": "2024-01-15T10:30:00Z",
            "valid_until": "2024-02-15T00:00:00Z",
            "total_amount": "1250.50",
            "is_expired": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Proforma Invoice Details
**Endpoint:** `GET /api/sales/proformas/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "customer": 1,
    "customer_name": "Jean Dupont",
    "proforma_number": "PRO-2024-001",
    "status": "sent",
    "proforma_date": "2024-01-15T10:30:00Z",
    "valid_until": "2024-02-15T00:00:00Z",
    "subtotal": "1042.08",
    "tax_rate": "20.00",
    "tax_amount": "208.42",
    "total_amount": "1250.50",
    "notes": "Devis pour commande urgente",
    "user": 1,
    "user_name": "Admin User",
    "is_draft": false,
    "is_sent": true,
    "is_accepted": false,
    "is_rejected": false,
    "is_expired": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Create Proforma Invoice
**Endpoint:** `POST /api/sales/proformas/`

**Required Permission:** `sales_proformas_create`

**Request Body:**
```json
{
    "customer": 1,
    "status": "draft",
    "proforma_date": "2024-01-15T10:30:00Z",
    "valid_until": "2024-02-15T00:00:00Z",
    "subtotal": "1042.08",
    "tax_rate": "20.00",
    "tax_amount": "208.42",
    "total_amount": "1250.50",
    "notes": "Devis pour commande urgente"
}
```

**Response (201 Created):** Same as Get Proforma Invoice Details

### 4. Update Proforma Invoice
**Endpoint:** `PUT /api/sales/proformas/{id}/` or `PATCH /api/sales/proformas/{id}/`

**Required Permission:** `sales_proformas_create`

**Request Body (PATCH - Partial Update):**
```json
{
    "status": "sent",
    "notes": "Devis envoyé au client"
}
```

**Response (200 OK):** Same as Get Proforma Invoice Details

### 5. Delete Proforma Invoice
**Endpoint:** `DELETE /api/sales/proformas/{id}/`

**Required Permission:** `sales_proformas_create`

**Response (204 No Content):** Empty response body

### 6. Proforma Invoice Status Management

#### Send Proforma
**Endpoint:** `POST /api/sales/proformas/{id}/send/`

**Required Permission:** `sales_proformas_create`

**Response (200 OK):** Updated proforma details

#### Accept Proforma
**Endpoint:** `POST /api/sales/proformas/{id}/accept/`

**Required Permission:** `sales_proformas_create`

**Response (200 OK):** Updated proforma details

#### Reject Proforma
**Endpoint:** `POST /api/sales/proformas/{id}/reject/`

**Required Permission:** `sales_proformas_create`

**Response (200 OK):** Updated proforma details

### 7. Proforma Invoice Filtering by Status

#### Draft Proformas
**Endpoint:** `GET /api/sales/proformas/draft/`

**Response (200 OK):** List of draft proformas

#### Sent Proformas
**Endpoint:** `GET /api/sales/proformas/sent/`

**Response (200 OK):** List of sent proformas

#### Accepted Proformas
**Endpoint:** `GET /api/sales/proformas/accepted/`

**Response (200 OK):** List of accepted proformas

#### Expired Proformas
**Endpoint:** `GET /api/sales/proformas/expired/`

**Response (200 OK):** List of expired proformas

### 8. Proformas Summary
**Endpoint:** `GET /api/sales/proformas/summary/`

**Description:** Get comprehensive proforma statistics.

**Response (200 OK):**
```json
{
    "total_proformas": 50,
    "draft_proformas": 5,
    "sent_proformas": 20,
    "accepted_proformas": 15,
    "rejected_proformas": 5,
    "expired_proformas": 5,
    "total_amount": 75000.00
}
```

---

## 💳 Payments Management

### 1. List Payments
**Endpoint:** `GET /api/sales/payments/`

**Description:** Retrieve all payments with optional filtering.

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `invoice` (int): Filter by invoice ID
- `payment_method` (string): Filter by payment method
- `user` (int): Filter by user ID
- `date_from` (date): Filter payments from date (YYYY-MM-DD)
- `date_to` (date): Filter payments to date (YYYY-MM-DD)
- `search` (string): Search in invoice number, reference, notes
- `ordering` (string): Order by field (created_at, payment_date, amount)

**Response (200 OK):**
```json
{
    "count": 200,
    "next": "http://localhost:8000/api/sales/payments/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "invoice_number": "INV-2024-001",
            "customer_name": "Jean Dupont",
            "payment_method": "bank_transfer",
            "amount": "1250.50",
            "payment_date": "2024-01-20T14:30:00Z",
            "reference": "TXN-123456",
            "created_at": "2024-01-20T14:30:00Z"
        }
    ]
}
```

### 2. Get Payment Details
**Endpoint:** `GET /api/sales/payments/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "invoice": 1,
    "invoice_number": "INV-2024-001",
    "customer_name": "Jean Dupont",
    "payment_method": "bank_transfer",
    "amount": "1250.50",
    "payment_date": "2024-01-20T14:30:00Z",
    "reference": "TXN-123456",
    "notes": "Paiement reçu via virement bancaire",
    "user": 1,
    "user_name": "Admin User",
    "created_at": "2024-01-20T14:30:00Z",
    "updated_at": "2024-01-20T14:30:00Z"
}
```

### 3. Create Payment
**Endpoint:** `POST /api/sales/payments/`

**Required Permission:** `sales_payments_create`

**Request Body:**
```json
{
    "invoice": 1,
    "payment_method": "bank_transfer",
    "amount": "1250.50",
    "payment_date": "2024-01-20T14:30:00Z",
    "reference": "TXN-123456",
    "notes": "Paiement reçu via virement bancaire"
}
```

**Response (201 Created):** Same as Get Payment Details

### 4. Update Payment
**Endpoint:** `PUT /api/sales/payments/{id}/` or `PATCH /api/sales/payments/{id}/`

**Required Permission:** `sales_payments_create`

**Request Body (PATCH - Partial Update):**
```json
{
    "amount": "1300.00",
    "notes": "Montant corrigé"
}
```

**Response (200 OK):** Same as Get Payment Details

### 5. Delete Payment
**Endpoint:** `DELETE /api/sales/payments/{id}/`

**Required Permission:** `sales_payments_create`

**Response (204 No Content):** Empty response body

### 6. Payments by Method
**Endpoint:** `GET /api/sales/payments/by_method/?method={payment_method}`

**Description:** Get payments filtered by payment method.

**Query Parameters:**
- `method` (string, required): Payment method (cash, bank_transfer, credit_card, check, other)

**Response (200 OK):** List of payments for the specified method

### 7. Payments Summary
**Endpoint:** `GET /api/sales/payments/summary/`

**Description:** Get comprehensive payment statistics.

**Response (200 OK):**
```json
{
    "total_payments": 200,
    "total_amount": 150000.00,
    "by_method": [
        {
            "payment_method": "bank_transfer",
            "count": 120,
            "total": 90000.00
        },
        {
            "payment_method": "credit_card",
            "count": 50,
            "total": 35000.00
        },
        {
            "payment_method": "cash",
            "count": 30,
            "total": 25000.00
        }
    ]
}
```

---

## 📊 Sales Analytics

### 1. Orders Summary for Dashboard
**Endpoint:** `GET /api/sales/orders/summary/`

**Description:** Get comprehensive order statistics for dashboard.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "orders": {
            "total": 150,
            "pending": 12,
            "confirmed": 45,
            "shipped": 38,
            "delivered": 55,
            "cancelled": 0
        },
        "revenue": {
            "today": 1500.00,
            "week": 10500.00,
            "month": 45000.00,
            "growth": 12.5
        },
        "conversion_rate": 36.67
    }
}
```

### 2. Invoices Summary for Dashboard
**Endpoint:** `GET /api/sales/invoices/summary/`

**Description:** Get comprehensive invoice statistics for dashboard.

**Response (200 OK):**
```json
{
    "success": true,
    "data": {
        "invoices": {
            "total": 120,
            "paid": 95,
            "pending": 25,
            "overdue": 5,
            "cancelled": 0
        },
        "amounts": {
            "total": 150000.00,
            "paid": 125000.00,
            "pending": 20000.00,
            "overdue": 5000.00
        },
        "collection_rate": 83.33
    }
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
        "quantity": ["La quantité doit être positive."],
        "unit_price": ["Le prix unitaire doit être positif."]
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
    "detail": "Vous n'avez pas la permission de voir les commandes",
    "required_permission": "sales_orders_view"
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

### Order Status Values
- `draft`: Brouillon
- `pending`: En attente
- `confirmed`: Confirmée
- `processing`: En cours
- `shipped`: Expédiée
- `delivered`: Livrée
- `cancelled`: Annulée

### Invoice Status Values
- `draft`: Brouillon
- `sent`: Envoyée
- `paid`: Payée
- `overdue`: En retard
- `cancelled`: Annulée

### Proforma Status Values
- `draft`: Brouillon
- `sent`: Envoyé
- `accepted`: Accepté
- `rejected`: Rejeté
- `expired`: Expiré

### Payment Method Values
- `cash`: Espèces
- `bank_transfer`: Virement bancaire
- `credit_card`: Carte de crédit
- `check`: Chèque
- `other`: Autre

### Field Validations

**Order:**
- `discount_rate`: 0-100%
- `tax_rate`: 0-100%
- `order_date`: Required
- `customer`: Required

**OrderItem:**
- `quantity`: Must be positive
- `unit_price`: Must be positive
- `product`: Required
- `variant`: Must belong to the product

**Invoice:**
- `due_date`: Must be after invoice_date
- `order`: Required

**ProformaInvoice:**
- `valid_until`: Must be after proforma_date
- `customer`: Required

**Payment:**
- `amount`: Must be positive
- `invoice`: Required
- `payment_method`: Required

---

## 🚀 Usage Examples

### JavaScript/Fetch Examples

**Get all orders:**
```javascript
const response = await fetch('/api/sales/orders/', {
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```

**Create a new order:**
```javascript
const response = await fetch('/api/sales/orders/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        customer: 1,
        status: 'pending',
        order_date: new Date().toISOString(),
        tax_rate: 20.00,
        items: [
            {
                product: 1,
                quantity: 2,
                unit_price: 500.00
            }
        ]
    })
});
const order = await response.json();
```

**Confirm an order:**
```javascript
const response = await fetch('/api/sales/orders/1/confirm/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const order = await response.json();
```

### cURL Examples

**Get order details:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/sales/orders/1/
```

**Create an invoice:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"order": 1, "status": "draft", "invoice_date": "2024-01-15T10:30:00Z", "due_date": "2024-02-15T00:00:00Z"}' \
     http://localhost:8000/api/sales/invoices/
```

**Get sales summary:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/sales/orders/summary/
```

---

## 📝 Notes

1. **Automatic Calculations**: Order totals, tax amounts, and discount amounts are calculated automatically
2. **Status Management**: Use the specific status change endpoints rather than updating the status field directly
3. **Permissions**: Each endpoint requires specific permissions for different actions
4. **Date Formats**: All dates are in ISO 8601 format (UTC)
5. **Validation**: All monetary fields are validated for positive values
6. **Relationships**: Orders are linked to customers, invoices to orders, payments to invoices

---

**🎉 Your Sales APIs are ready for integration!**

This comprehensive API specification covers all sales management functionality in the Baobab ERP system, including orders, invoices, proformas, and payments with full CRUD operations and advanced filtering capabilities.
