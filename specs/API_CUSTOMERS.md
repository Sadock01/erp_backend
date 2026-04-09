# API Customers - Documentation

## Endpoints disponibles

### Base URL
```
/api/customers/
```

### Méthodes HTTP supportées

#### 1. **GET /api/customers/**
- **Description** : Liste tous les clients
- **Paramètres de requête** :
  - `is_active` : Filtre par statut actif (true/false)
  - `country` : Filtre par pays
  - `company` : Filtre par entreprise
  - `search` : Recherche dans nom, email, téléphone, entreprise
  - `ordering` : Tri (first_name, last_name, email, created_at, updated_at)
  - `page` : Pagination

#### 2. **POST /api/customers/**
- **Description** : Créer un nouveau client
- **Body** :
```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "phone": "0123456789",
  "company": "Entreprise ABC",
  "address": "123 Rue de la Paix",
  "city": "Paris",
  "postal_code": "75001",
  "country": "France",
  "notes": "Client VIP"
}
```

#### 3. **GET /api/customers/{id}/**
- **Description** : Récupérer un client spécifique

#### 4. **PUT /api/customers/{id}/**
- **Description** : Mettre à jour un client complet

#### 5. **PATCH /api/customers/{id}/**
- **Description** : Mettre à jour partiellement un client

#### 6. **DELETE /api/customers/{id}/**
- **Description** : Désactiver un client (soft delete)

### Actions personnalisées

#### 7. **GET /api/customers/active/**
- **Description** : Liste uniquement les clients actifs

#### 8. **GET /api/customers/inactive/**
- **Description** : Liste uniquement les clients inactifs

#### 9. **POST /api/customers/{id}/activate/**
- **Description** : Activer un client

#### 10. **POST /api/customers/{id}/deactivate/**
- **Description** : Désactiver un client

#### 11. **GET /api/customers/search/?q=terme**
- **Description** : Recherche avancée de clients

## Exemples d'utilisation

### Créer un client
```bash
curl -X POST http://localhost:8000/api/customers/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{
    "first_name": "Marie",
    "last_name": "Martin",
    "email": "marie.martin@example.com",
    "phone": "0987654321",
    "company": "Société XYZ"
  }'
```

### Lister les clients actifs
```bash
curl -X GET "http://localhost:8000/api/customers/active/" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Rechercher des clients
```bash
curl -X GET "http://localhost:8000/api/customers/search/?q=marie" \
  -H "Authorization: Token YOUR_TOKEN"
```

### Filtrer par pays
```bash
curl -X GET "http://localhost:8000/api/customers/?country=France" \
  -H "Authorization: Token YOUR_TOKEN"
```

## Codes de réponse

- **200** : Succès
- **201** : Créé avec succès
- **400** : Erreur de validation
- **401** : Non authentifié
- **403** : Non autorisé
- **404** : Client non trouvé
- **500** : Erreur serveur

## Authentification

L'API utilise l'authentification par token Django REST Framework. Incluez le token dans l'en-tête :

```
Authorization: Token YOUR_TOKEN
```
