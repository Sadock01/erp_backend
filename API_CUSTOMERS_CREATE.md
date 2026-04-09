# API de Création des Clients - Spécifications

## Vue d'ensemble
L'API de création des clients permet de créer de nouveaux clients dans le système ERP Baobab. Elle inclut la validation des données, la gestion des permissions et la vérification d'unicité des emails.

## Endpoint

### POST /api/customers/

**Description :** Créer un nouveau client

**Authentification :** Token requis

**Permissions :** `customers_create`

---

## Headers

```http
Authorization: Token <your_token>
Content-Type: application/json
```

---

## Paramètres de la requête

### Champs obligatoires

| Champ | Type | Description | Validation |
|-------|------|-------------|------------|
| `first_name` | string | Prénom du client | Max 100 caractères |
| `last_name` | string | Nom de famille du client | Max 100 caractères |
| `email` | string | Adresse email du client | Format email valide, unique |

### Champs optionnels

| Champ | Type | Description | Validation |
|-------|------|-------------|------------|
| `phone` | string | Numéro de téléphone | Max 20 caractères |
| `company` | string | Nom de l'entreprise | Max 200 caractères |
| `address` | string | Adresse complète | Texte libre |
| `city` | string | Ville | Max 100 caractères |
| `postal_code` | string | Code postal | Max 10 caractères |
| `country` | string | Pays | Max 100 caractères, défaut: "France" |
| `notes` | string | Notes supplémentaires | Texte libre |

---

## Exemple de requête

```http
POST /api/customers/
Authorization: Token 1e367e68c1a81d5ed312eae081c2faba21d40676
Content-Type: application/json

{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean.dupont@example.com",
    "phone": "+33 6 12 34 56 78",
    "company": "Entreprise ABC",
    "address": "123 Rue de la Paix",
    "city": "Paris",
    "postal_code": "75001",
    "country": "France",
    "notes": "Client VIP, préfère être contacté par email"
}
```

---

## Réponses

### ✅ Succès (201 Created)

```json
{
    "id": 1,
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean.dupont@example.com",
    "phone": "+33 6 12 34 56 78",
    "company": "Entreprise ABC",
    "address": "123 Rue de la Paix",
    "city": "Paris",
    "postal_code": "75001",
    "country": "France",
    "is_active": true,
    "notes": "Client VIP, préfère être contacté par email",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

### ❌ Erreur de validation (400 Bad Request)

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

### ❌ Permission refusée (403 Forbidden)

```json
{
    "error": "Permission refusée",
    "detail": "Vous n'avez pas la permission de créer des clients",
    "required_permission": "customers_create"
}
```

### ❌ Non authentifié (401 Unauthorized)

```json
{
    "detail": "Informations d'authentification non fournies."
}
```

---

## Règles de validation

### 1. Email unique
- L'email doit être unique dans la base de données
- Format email valide requis
- Vérification automatique lors de la création

### 2. Champs obligatoires
- `first_name` : Prénom requis
- `last_name` : Nom de famille requis  
- `email` : Email requis et unique

### 3. Valeurs par défaut
- `is_active` : `true` (client actif par défaut)
- `country` : "France" si non spécifié

### 4. Longueurs maximales
- `first_name` : 100 caractères
- `last_name` : 100 caractères
- `email` : 255 caractères
- `phone` : 20 caractères
- `company` : 200 caractères
- `city` : 100 caractères
- `postal_code` : 10 caractères
- `country` : 100 caractères

---

## Exemples d'utilisation

### Création d'un client individuel

```bash
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Authorization: Token 1e367e68c1a81d5ed312eae081c2faba21d40676" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Marie",
    "last_name": "Martin",
    "email": "marie.martin@email.com",
    "phone": "+33 6 98 76 54 32"
  }'
```

### Création d'un client entreprise

```bash
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Authorization: Token 1e367e68c1a81d5ed312eae081c2faba21d40676" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Pierre",
    "last_name": "Durand",
    "email": "p.durand@entreprise.com",
    "company": "Entreprise XYZ",
    "address": "456 Avenue des Champs",
    "city": "Lyon",
    "postal_code": "69001",
    "country": "France"
  }'
```

### Création minimale (champs obligatoires seulement)

```bash
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Authorization: Token 1e367e68c1a81d5ed312eae081c2faba21d40676" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Sophie",
    "last_name": "Bernard",
    "email": "sophie.bernard@test.com"
  }'
```

---

## Codes de statut HTTP

| Code | Description |
|------|-------------|
| `201` | Client créé avec succès |
| `400` | Données invalides ou email déjà existant |
| `401` | Non authentifié |
| `403` | Permission refusée |
| `500` | Erreur serveur |

---

## Notes techniques

- **Modèle :** `Customer` dans `apps.customers.models`
- **Serializer :** `CustomerCreateSerializer` dans `apps.customers.serializers`
- **View :** `CustomerViewSet.create()` dans `apps.customers.views`
- **Permission :** Vérifiée via `user_has_permission(request.user, 'customers_create')`
- **Validation :** Email unique vérifié automatiquement
- **Timestamps :** `created_at` et `updated_at` ajoutés automatiquement

---

## Intégration avec d'autres APIs

Une fois créé, le client peut être :
- **Consulté :** `GET /api/customers/{id}/`
- **Modifié :** `PUT/PATCH /api/customers/{id}/`
- **Supprimé :** `DELETE /api/customers/{id}/`
- **Listé :** `GET /api/customers/`
- **Analysé :** `GET /api/customers/analytics/kpis/`
