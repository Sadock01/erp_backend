# 🏢 Spécifications API Entreprise - Baobab ERP

## 📋 Vue d'ensemble

Cette documentation décrit les APIs de gestion des entreprises pour l'ERP Baobab. Ces APIs permettent de récupérer les informations des entreprises et de gérer l'accès aux données d'entreprise.

---

## 🌐 Base URL

```
http://localhost:8000/api/
```

---

## 🏢 1. Récupérer mon entreprise

### Endpoint
```
GET /api/companies/my/
```

### Description
Récupérer les informations de l'entreprise de l'utilisateur connecté.

### Authentification
- **Requis** : Token d'authentification

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Réponse de succès (200 OK)
```json
{
  "id": 1,
  "name": "Mon Entreprise SARL",
  "logo": null,
  "logo_url": null,
  "description": "Ma belle entreprise de vente en ligne",
  "email": "contact@monentreprise.com",
  "phone": "01 23 45 67 89",
  "address": "123 Rue de la Paix",
  "city": "Paris",
  "postal_code": "75001",
  "country": "France",
  "website": "https://monentreprise.com",
  "tax_number": "FR12345678901",
  "registration_number": "12345678901234",
  "is_active": true,
  "settings": {},
  "user_count": 3,
  "admin_count": 1,
  "full_address": "123 Rue de la Paix, 75001 Paris, France",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Réponse d'erreur (404 Not Found)
```json
{
  "error": "Profil non trouvé",
  "detail": "Vous n'êtes associé à aucune entreprise"
}
```

### Codes d'erreur possibles
- `401` : Non authentifié
- `404` : Utilisateur non associé à une entreprise
- `500` : Erreur serveur

---

## 🏢 2. Récupérer une entreprise par ID

### Endpoint
```
GET /api/companies/{company_id}/
```

### Description
Récupérer les informations d'une entreprise spécifique. L'utilisateur doit soit appartenir à cette entreprise, soit avoir la permission `companies_view_all`.

### Authentification
- **Requis** : Token d'authentification

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Paramètres d'URL
- `company_id` (integer) : ID de l'entreprise

### Réponse de succès (200 OK)
```json
{
  "id": 1,
  "name": "Mon Entreprise SARL",
  "logo": null,
  "logo_url": null,
  "description": "Ma belle entreprise de vente en ligne",
  "email": "contact@monentreprise.com",
  "phone": "01 23 45 67 89",
  "address": "123 Rue de la Paix",
  "city": "Paris",
  "postal_code": "75001",
  "country": "France",
  "website": "https://monentreprise.com",
  "tax_number": "FR12345678901",
  "registration_number": "12345678901234",
  "is_active": true,
  "settings": {},
  "user_count": 3,
  "admin_count": 1,
  "full_address": "123 Rue de la Paix, 75001 Paris, France",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Réponse d'erreur (404 Not Found)
```json
{
  "error": "Entreprise non trouvée",
  "detail": "L'entreprise avec l'ID 999 n'existe pas ou n'est pas active"
}
```

### Réponse d'erreur (403 Forbidden)
```json
{
  "error": "Accès refusé",
  "detail": "Vous n'avez pas accès à cette entreprise"
}
```

### Codes d'erreur possibles
- `401` : Non authentifié
- `403` : Accès refusé (pas membre de l'entreprise et pas de permission)
- `404` : Entreprise non trouvée
- `500` : Erreur serveur

---

## 🏢 3. Lister toutes les entreprises

### Endpoint
```
GET /api/companies/
```

### Description
Lister toutes les entreprises actives. Nécessite la permission `companies_view_all`.

### Authentification
- **Requis** : Token d'authentification
- **Permission** : `companies_view_all`

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Réponse de succès (200 OK)
```json
[
  {
    "id": 1,
    "name": "Mon Entreprise SARL",
    "logo_url": "http://localhost:8000/media/companies/logos/logo1.jpg",
    "email": "contact@monentreprise.com",
    "phone": "01 23 45 67 89",
    "city": "Paris",
    "country": "France",
    "is_active": true,
    "user_count": 3,
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "Autre Entreprise SAS",
    "logo_url": null,
    "email": "contact@autreentreprise.com",
    "phone": "01 98 76 54 32",
    "city": "Lyon",
    "country": "France",
    "is_active": true,
    "user_count": 5,
    "created_at": "2024-01-16T14:20:00Z"
  }
]
```

### Réponse d'erreur (403 Forbidden)
```json
{
  "error": "Permission refusée",
  "detail": "Vous n'avez pas la permission de voir toutes les entreprises",
  "required_permission": "companies_view_all"
}
```

### Codes d'erreur possibles
- `401` : Non authentifié
- `403` : Permission refusée
- `500` : Erreur serveur

---

## 📊 Champs de réponse

### Champs de base
- `id` (integer) : ID unique de l'entreprise
- `name` (string) : Nom de l'entreprise
- `description` (string) : Description de l'entreprise
- `email` (string) : Email de contact
- `phone` (string) : Téléphone
- `address` (string) : Adresse
- `city` (string) : Ville
- `postal_code` (string) : Code postal
- `country` (string) : Pays
- `website` (string) : Site web
- `tax_number` (string) : Numéro de TVA
- `registration_number` (string) : Numéro d'enregistrement
- `is_active` (boolean) : Statut actif
- `settings` (object) : Paramètres personnalisés
- `created_at` (datetime) : Date de création
- `updated_at` (datetime) : Date de modification

### Champs calculés
- `logo_url` (string) : URL complète du logo (si disponible)
- `user_count` (integer) : Nombre d'utilisateurs dans l'entreprise
- `admin_count` (integer) : Nombre d'admins dans l'entreprise
- `full_address` (string) : Adresse complète formatée

---

## 🔐 Permissions et accès

### Niveaux d'accès
1. **Utilisateur standard** : Peut voir uniquement son entreprise (`/companies/my/`)
2. **Membre d'entreprise** : Peut voir son entreprise et les entreprises auxquelles il a accès
3. **Super Admin** : Peut voir toutes les entreprises (`/companies/`)

### Permissions requises
- `companies_view_all` : Voir toutes les entreprises (Super Admin uniquement)

---

## 🧪 Exemples de test

### Récupérer mon entreprise
```bash
curl -X GET http://localhost:8000/api/companies/my/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Récupérer une entreprise spécifique
```bash
curl -X GET http://localhost:8000/api/companies/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Lister toutes les entreprises (Super Admin)
```bash
curl -X GET http://localhost:8000/api/companies/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## 📝 Notes importantes

- **Authentification requise** : Tous les endpoints nécessitent un token valide
- **Accès restreint** : Les utilisateurs ne peuvent voir que leur entreprise par défaut
- **Permissions** : Seuls les Super Admins peuvent voir toutes les entreprises
- **Entreprises actives** : Seules les entreprises actives sont retournées
- **URLs de logo** : Les URLs de logo sont absolues et incluent le domaine complet
- **Compteurs** : Les compteurs d'utilisateurs et d'admins sont calculés en temps réel

---

## 🔄 Cas d'usage

1. **Dashboard utilisateur** : Afficher les informations de l'entreprise de l'utilisateur
2. **Gestion d'entreprise** : Permettre aux admins de voir les statistiques de leur entreprise
3. **Administration système** : Permettre aux Super Admins de gérer toutes les entreprises
4. **Intégration** : Récupérer les informations d'entreprise pour d'autres modules
