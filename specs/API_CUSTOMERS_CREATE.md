# API Customers - Création de Client

## Endpoint
```
POST /api/customers/
```

## Description
Crée un nouveau client dans le système. Le client est automatiquement associé à l'entreprise de l'utilisateur connecté.

## Authentification
- **Type** : Token Authentication
- **Header** : `Authorization: Token <token>`
- **Permission requise** : `customers_create`

## Paramètres de la requête

### Headers
| Nom | Type | Requis | Description |
|-----|------|--------|-------------|
| `Authorization` | string | Oui | Token d'authentification |
| `Content-Type` | string | Oui | `application/json` |

### Body (JSON)
| Champ | Type | Requis | Description |
|-------|------|--------|-------------|
| `first_name` | string | Oui | Prénom du client (max 100 caractères) |
| `last_name` | string | Oui | Nom de famille du client (max 100 caractères) |
| `email` | string | Oui | Adresse email du client (format email valide) |
| `phone` | string | Non | Numéro de téléphone du client (max 20 caractères) |
| `client_company` | string | Non | Nom de l'entreprise du client (max 200 caractères) |
| `address` | string | Non | Adresse complète du client |
| `city` | string | Non | Ville du client (max 100 caractères) |
| `postal_code` | string | Non | Code postal du client (max 20 caractères) |
| `country` | string | Non | Pays du client (max 100 caractères) |
| `notes` | string | Non | Notes supplémentaires sur le client |

## Réponses

### Succès (201 Created)
```json
{
  "id": 8,
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "phone": "0123456789",
  "client_company": "Entreprise ABC",
  "address": "123 Rue de la Paix",
  "city": "Paris",
  "postal_code": "75001",
  "country": "France",
  "notes": "Client VIP",
  "is_active": true,
  "created_at": "2025-10-10T12:15:11.009670+02:00",
  "updated_at": "2025-10-10T12:15:11.009720+02:00"
}
```

### Erreur - Permission refusée (403 Forbidden)
```json
{
  "error": "Permission refusée",
  "detail": "Vous n'avez pas la permission de créer des clients",
  "required_permission": "customers_create"
}
```

### Erreur - Validation (400 Bad Request)
```json
{
  "email": [
    "Un client avec cet email existe déjà."
  ],
  "first_name": [
    "Ce champ est obligatoire."
  ]
}
```

### Erreur - Profil utilisateur non trouvé (400 Bad Request)
```json
{
  "error": "Profil utilisateur non trouvé",
  "detail": "Vous devez être associé à une entreprise pour créer des clients"
}
```

### Erreur - Contexte manquant (400 Bad Request)
```json
{
  "error": "Contexte de requête manquant",
  "detail": "Impossible de déterminer l'entreprise de l'utilisateur"
}
```

## Champs de la réponse

### Champs retournés
| Champ | Type | Description |
|-------|------|-------------|
| `id` | integer | Identifiant unique du client créé |
| `first_name` | string | Prénom du client |
| `last_name` | string | Nom de famille du client |
| `email` | string | Adresse email du client |
| `phone` | string | Numéro de téléphone du client |
| `client_company` | string | Nom de l'entreprise du client |
| `address` | string | Adresse complète du client |
| `city` | string | Ville du client |
| `postal_code` | string | Code postal du client |
| `country` | string | Pays du client |
| `notes` | string | Notes supplémentaires sur le client |
| `is_active` | boolean | Statut actif du client (toujours `true` à la création) |
| `created_at` | datetime | Date et heure de création |
| `updated_at` | datetime | Date et heure de dernière modification |

## Comportement spécial

### Association automatique à l'entreprise
- Le client créé est **automatiquement associé** à l'entreprise de l'utilisateur connecté
- Le champ `company` n'est pas requis dans la requête car il est assigné automatiquement
- L'utilisateur ne peut créer des clients que pour sa propre entreprise

### Validation de l'email
- L'email doit être unique dans le système
- L'email doit respecter le format email standard
- Si un client avec le même email existe déjà, une erreur de validation est retournée

## Exemples d'utilisation

### Exemple 1 : Création d'un client simple
```bash
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Authorization: Token 88be7157c05569fd4ff5a1cd03a92258264a24e3" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marie",
    "last_name": "Martin",
    "email": "marie.martin@example.com",
    "phone": "0123456789",
    "city": "Lyon",
    "country": "France"
  }'
```

### Exemple 2 : Création d'un client avec entreprise
```bash
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Authorization: Token 88be7157c05569fd4ff5a1cd03a92258264a24e3" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Pierre",
    "last_name": "Durand",
    "email": "pierre.durand@entreprise.com",
    "phone": "0987654321",
    "client_company": "Entreprise XYZ",
    "address": "456 Avenue des Champs",
    "city": "Marseille",
    "postal_code": "13001",
    "country": "France",
    "notes": "Client important, négocier les prix"
  }'
```

## Codes de statut HTTP

| Code | Description |
|------|-------------|
| 201 | Client créé avec succès |
| 400 | Erreur de validation ou profil utilisateur manquant |
| 401 | Non authentifié |
| 403 | Permission refusée |
| 500 | Erreur serveur interne |

## Notes importantes

1. **Isolation par entreprise** : Chaque utilisateur ne peut créer des clients que pour son entreprise
2. **Email unique** : L'email doit être unique dans tout le système, pas seulement dans l'entreprise
3. **Champs optionnels** : Tous les champs sauf `first_name`, `last_name` et `email` sont optionnels
4. **Association automatique** : Le client est automatiquement associé à l'entreprise de l'utilisateur connecté
5. **Validation stricte** : Les emails sont validés pour le format et l'unicité

## Sécurité

- **Authentification requise** : Seuls les utilisateurs authentifiés peuvent créer des clients
- **Permission requise** : L'utilisateur doit avoir la permission `customers_create`
- **Isolation des données** : Les clients sont automatiquement associés à l'entreprise de l'utilisateur
- **Validation des données** : Toutes les données sont validées avant la création
