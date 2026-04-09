# 👥 API Specifications - User Management (Admin)
## Baobab ERP System

This document provides comprehensive specifications for all user management APIs for administrators in the Baobab ERP system.

---

## 🌐 Base URL
```
http://localhost:8000/api/permissions/
```
**Production:** `https://your-domain.com/api/permissions/`

---

## 🔐 Authentication
All API endpoints require authentication using Token authentication:

```http
Authorization: Token <your_token_here>
```

**Required Permission:** `users_manage`

**How to get a token:**
```http
POST /api/auth/login/x
Content-Type: application/json

{
    "email": "your_email@example.com",
    "password": "your_password"
}
```

---

## 📋 Table of Contents
1. [User Management (CRUD)](#user-management-crud)
2. [User Role Management](#user-role-management)
3. [User Status Management](#user-status-management)
4. [Bulk Operations](#bulk-operations)
5. [User Analytics](#user-analytics)
6. [Error Handling](#error-handling)
7. [Data Models](#data-models)

---

## 👤 User Management (CRUD)

### 1. List Users
**Endpoint:** `GET /api/permissions/users/`

**Description:** Retrieve all users with optional filtering and pagination.

**Required Permission:** `users_manage`

**Query Parameters:**
- `page` (int): Page number for pagination
- `limit` (int): Number of items per page
- `is_active` (boolean): Filter by active status
- `is_staff` (boolean): Filter by staff status
- `is_superuser` (boolean): Filter by superuser status
- `search` (string): Search in username, email, first_name, last_name
- `ordering` (string): Order by field (username, email, date_joined, last_login)

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/permissions/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "admin",
            "email": "admin@baobab-erp.com",
            "first_name": "Admin",
            "last_name": "User",
            "is_active": true,
            "is_staff": true,
            "is_superuser": true,
            "date_joined": "2024-01-15T10:30:00Z",
            "last_login": "2024-01-20T14:30:00Z",
            "roles_count": 2,
            "last_login_display": "20/01/2024 14:30",
            "date_joined_display": "15/01/2024 10:30"
        }
    ]
}
```

### 2. Get User Details
**Endpoint:** `GET /api/permissions/users/{id}/`

**Required Permission:** `users_manage`

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "admin",
    "email": "admin@baobab-erp.com",
    "first_name": "Admin",
    "last_name": "User",
    "is_active": true,
    "is_staff": true,
    "is_superuser": true,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-20T14:30:00Z"
}
```

### 3. Create User
**Endpoint:** `POST /api/permissions/users/`

**Required Permission:** `users_manage`

**Request Body:**
```json
{
    "username": "new_user",
    "email": "user@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

**Response (201 Created):** Same as Get User Details

### 4. Update User
**Endpoint:** `PUT /api/permissions/users/{id}/` or `PATCH /api/permissions/users/{id}/`

**Required Permission:** `users_manage`

**Request Body (PATCH - Partial Update):**
```json
{
    "first_name": "John Updated",
    "last_name": "Doe Updated",
    "is_active": false
}
```

**Response (200 OK):** Same as Get User Details

### 5. Delete User
**Endpoint:** `DELETE /api/permissions/users/{id}/`

**Required Permission:** `users_manage`

**Response (204 No Content):** Empty response body

---

## 🔍 User Filtering

### Active Users
**Endpoint:** `GET /api/permissions/users/active/`

**Required Permission:** `users_manage`

**Description:** List only active users

**Response (200 OK):** List of active users

### Staff Users
**Endpoint:** `GET /api/permissions/users/staff/`

**Required Permission:** `users_manage`

**Description:** List only staff users

**Response (200 OK):** List of staff users

---

## 🔐 User Status Management

### Activate User
**Endpoint:** `POST /api/permissions/users/{id}/activate/`

**Required Permission:** `users_manage`

**Response (200 OK):** Updated user details

### Deactivate User
**Endpoint:** `POST /api/permissions/users/{id}/deactivate/`

**Required Permission:** `users_manage`

**Response (200 OK):** Updated user details

### Reset Password
**Endpoint:** `POST /api/permissions/users/{id}/reset_password/`

**Required Permission:** `users_manage`

**Request Body:**
```json
{
    "new_password": "newsecurepassword123"
}
```

**Response (200 OK):**
```json
{
    "message": "Mot de passe réinitialisé avec succès"
}
```

---

## 👥 User Role Management

### 1. Get User Roles
**Endpoint:** `GET /api/permissions/users/{id}/roles/`

**Required Permission:** `users_manage`

**Description:** List all active roles for a user

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "user": 1,
        "role": 2,
        "assigned_by": 1,
        "assigned_at": "2024-01-15T10:30:00Z",
        "expires_at": null,
        "is_active": true,
        "user_name": "admin",
        "user_email": "admin@baobab-erp.com",
        "role_name": "Sales Manager",
        "role_color": "#28a745",
        "assigned_by_name": "admin",
        "is_expired": false,
        "days_until_expiry": null,
        "notes": "Rôle assigné pour la gestion des ventes",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
]
```

### 2. Assign Role to User
**Endpoint:** `POST /api/permissions/users/{id}/assign_role/`

**Required Permission:** `users_manage`

**Request Body:**
```json
{
    "role_id": 2,
    "expires_at": "2024-12-31T23:59:59Z",
    "notes": "Rôle temporaire pour un projet"
}
```

**Response (201 Created):** UserRole details

### 3. Remove Role from User
**Endpoint:** `POST /api/permissions/users/{id}/remove_role/`

**Required Permission:** `users_manage`

**Request Body:**
```json
{
    "role_id": 2
}
```

**Response (200 OK):**
```json
{
    "message": "Rôle retiré avec succès"
}
```

---

## 🚀 Advanced User Creation

### Create User with Roles
**Endpoint:** `POST /api/permissions/admin/create-user/`

**Required Permission:** `users_manage`

**Description:** Create a new user and assign roles in one operation

**Request Body:**
```json
{
    "username": "manager1",
    "email": "manager@company.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "Marie",
    "last_name": "Martin",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "role_ids": [2, 3, 4]
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 5,
        "username": "manager1",
        "email": "manager@company.com",
        "first_name": "Marie",
        "last_name": "Martin",
        "is_active": true,
        "is_staff": false,
        "is_superuser": false,
        "date_joined": "2024-01-20T10:30:00Z",
        "last_login": null
    },
    "message": "Utilisateur créé avec succès"
}
```

---

## 📊 Bulk Operations

### Bulk Assign Roles
**Endpoint:** `POST /api/permissions/admin/bulk-assign-roles/`

**Required Permission:** `users_manage`

**Description:** Assign a role to multiple users at once

**Request Body:**
```json
{
    "user_ids": [1, 2, 3, 4, 5],
    "role_id": 2,
    "expires_at": "2024-12-31T23:59:59Z",
    "notes": "Rôle temporaire pour projet spécial"
}
```

**Response (200 OK):**
```json
{
    "message": "Rôle assigné à 4 utilisateur(s)",
    "assigned_count": 4,
    "errors": [
        "L'utilisateur admin a déjà ce rôle"
    ]
}
```

---

## 📈 User Analytics

### Users Summary
**Endpoint:** `GET /api/permissions/users/summary/`

**Required Permission:** `users_manage`

**Description:** Get comprehensive user statistics

**Response (200 OK):**
```json
{
    "total_users": 25,
    "active_users": 23,
    "inactive_users": 2,
    "staff_users": 5,
    "superusers": 1,
    "recent_users": 3
}
```

### User Detailed Permissions
**Endpoint:** `GET /api/permissions/admin/user-permissions/{user_id}/`

**Required Permission:** `users_manage`

**Description:** Get detailed permissions breakdown for a user

**Response (200 OK):**
```json
{
    "user": {
        "id": 1,
        "username": "admin",
        "email": "admin@baobab-erp.com",
        "first_name": "Admin",
        "last_name": "User",
        "is_active": true,
        "is_staff": true,
        "is_superuser": true,
        "date_joined": "2024-01-15T10:30:00Z",
        "last_login": "2024-01-20T14:30:00Z"
    },
    "roles": [
        {
            "id": 1,
            "name": "Super Admin",
            "description": "Administrateur système",
            "level": 0,
            "color": "#dc3545",
            "icon": "fas fa-user-shield",
            "user_count": 1,
            "is_active": true
        }
    ],
    "permissions_by_app": {
        "customers": {
            "granted": [
                {
                    "id": 1,
                    "name": "Voir les clients",
                    "codename": "customers_view",
                    "action": "view",
                    "resource": "customer"
                },
                {
                    "id": 2,
                    "name": "Créer des clients",
                    "codename": "customers_create",
                    "action": "create",
                    "resource": "customer"
                }
            ],
            "denied": []
        },
        "sales": {
            "granted": [
                {
                    "id": 10,
                    "name": "Gérer les commandes",
                    "codename": "sales_orders_manage",
                    "action": "manage",
                    "resource": "order"
                }
            ],
            "denied": []
        }
    },
    "total_granted": 25,
    "total_denied": 0,
    "total_roles": 1
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
        "username": ["Ce nom d'utilisateur est déjà utilisé."],
        "email": ["Cet email est déjà utilisé."],
        "password_confirm": ["Les mots de passe ne correspondent pas."]
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
    "detail": "Vous n'avez pas la permission de voir les utilisateurs",
    "required_permission": "users_manage"
}
```

**404 Not Found:**
```json
{
    "error": "Utilisateur introuvable"
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

### User Fields
- `id`: Unique identifier
- `username`: Unique username (required)
- `email`: Email address (required, unique)
- `first_name`: First name (optional)
- `last_name`: Last name (optional)
- `is_active`: Active status (boolean)
- `is_staff`: Staff status (boolean)
- `is_superuser`: Superuser status (boolean)
- `date_joined`: Registration date (read-only)
- `last_login`: Last login date (read-only)

### UserRole Fields
- `id`: Unique identifier
- `user`: User ID (required)
- `role`: Role ID (required)
- `assigned_by`: User who assigned the role
- `assigned_at`: Assignment date (auto-generated)
- `expires_at`: Expiration date (optional)
- `is_active`: Active status (boolean)
- `notes`: Additional notes (optional)

### Field Validations

**User Creation:**
- `username`: Required, unique, max 150 characters
- `email`: Required, unique, valid email format
- `password`: Required, min 8 characters
- `password_confirm`: Must match password
- `first_name`: Max 30 characters
- `last_name`: Max 30 characters

**Role Assignment:**
- `role_id`: Required, must exist
- `expires_at`: Optional, must be future date if provided
- `notes`: Optional, max 500 characters

---

## 🚀 Usage Examples

### JavaScript/Fetch Examples

**Get all users:**
```javascript
const response = await fetch('/api/permissions/users/', {
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
```

**Create a new user:**
```javascript
const response = await fetch('/api/permissions/users/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'new_user',
        email: 'user@example.com',
        password: 'securepassword123',
        password_confirm: 'securepassword123',
        first_name: 'John',
        last_name: 'Doe',
        is_active: true
    })
});
const user = await response.json();
```

**Create user with roles:**
```javascript
const response = await fetch('/api/permissions/admin/create-user/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        username: 'manager1',
        email: 'manager@company.com',
        password: 'securepass123',
        password_confirm: 'securepass123',
        first_name: 'Marie',
        last_name: 'Martin',
        role_ids: [2, 3, 4]
    })
});
const result = await response.json();
```

**Assign role to user:**
```javascript
const response = await fetch('/api/permissions/users/1/assign_role/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        role_id: 2,
        expires_at: '2024-12-31T23:59:59Z',
        notes: 'Rôle temporaire'
    })
});
const userRole = await response.json();
```

**Bulk assign roles:**
```javascript
const response = await fetch('/api/permissions/admin/bulk-assign-roles/', {
    method: 'POST',
    headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        user_ids: [1, 2, 3, 4],
        role_id: 2,
        expires_at: '2024-12-31T23:59:59Z',
        notes: 'Rôle temporaire pour projet'
    })
});
const result = await response.json();
```

### cURL Examples

**Get user details:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/permissions/users/1/
```

**Create a user:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"username": "new_user", "email": "user@example.com", "password": "securepass123", "password_confirm": "securepass123", "first_name": "John", "last_name": "Doe"}' \
     http://localhost:8000/api/permissions/users/
```

**Activate a user:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/permissions/users/1/activate/
```

**Reset user password:**
```bash
curl -X POST \
     -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     -d '{"new_password": "newpassword123"}' \
     http://localhost:8000/api/permissions/users/1/reset_password/
```

**Get user summary:**
```bash
curl -H "Authorization: Token your_token_here" \
     -H "Content-Type: application/json" \
     http://localhost:8000/api/permissions/users/summary/
```

---

## 📝 Notes

1. **Password Security**: Passwords are automatically hashed using Django's built-in password hashing
2. **Role Management**: Users can have multiple roles, roles can have expiration dates
3. **Permissions**: All endpoints require the `users_manage` permission
4. **Audit Trail**: All role assignments are tracked with who assigned them and when
5. **Bulk Operations**: Use bulk endpoints for efficiency when managing multiple users
6. **Validation**: All user data is validated before creation/update
7. **Soft Delete**: User deletion is permanent - use deactivation instead for temporary removal

---

## 🔐 Required Permissions

### User Management
- `users_manage`: Full management of users (create, read, update, delete, activate, deactivate, reset password)

### Role Management
- `users_manage`: Required for all role assignment operations

---

**🎉 Your User Management APIs are ready for integration!**

This comprehensive API specification covers all user management functionality for administrators in the Baobab ERP system, including CRUD operations, role management, bulk operations, and detailed analytics with full security controls.
