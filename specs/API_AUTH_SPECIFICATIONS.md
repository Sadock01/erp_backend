# 🔐 Spécifications API Authentification - Baobab ERP

## 📋 Vue d'ensemble

Cette documentation décrit les APIs d'authentification pour l'ERP Baobab, incluant l'inscription, la connexion, la déconnexion et la gestion des profils utilisateur.

---

## 🌐 Base URL

```
http://localhost:8000/api/
```

---

## 🔑 1. Inscription (Register)

### Endpoint
```
POST /api/auth/register/
```

### Description
Créer un nouveau compte utilisateur dans le système.

### Headers
```
Content-Type: application/json
```

### Body (JSON)
```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "motdepasse123",
  "password_confirm": "motdepasse123",
  "first_name": "John",
  "last_name": "Doe"
}
```

### Champs requis
- `username` (string, max 150 caractères) : Nom d'utilisateur unique
- `email` (string, format email) : Adresse email unique
- `password` (string, min 8 caractères) : Mot de passe
- `password_confirm` (string) : Confirmation du mot de passe

### Champs optionnels
- `first_name` (string, max 30 caractères) : Prénom
- `last_name` (string, max 30 caractères) : Nom de famille

### Réponse de succès (201 Created)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "message": "Inscription réussie"
}
```

### Réponse d'erreur (400 Bad Request)
```json
{
  "username": ["Ce nom d'utilisateur est déjà utilisé."],
  "email": ["Cet email est déjà utilisé."],
  "password": ["Ce champ est requis."],
  "password_confirm": ["Les mots de passe ne correspondent pas."]
}
```

### Codes d'erreur possibles
- `400` : Données invalides ou utilisateur déjà existant
- `500` : Erreur serveur

---

## 🔐 2. Connexion (Login)

### Endpoint
```
POST /api/auth/login/
```

### Description
Authentifier un utilisateur existant avec son email et mot de passe.

### Headers
```
Content-Type: application/json
```

### Body (JSON)
```json
{
  "email": "john.doe@example.com",
  "password": "motdepasse123"
}
```

### Champs requis
- `email` (string, format email) : Adresse email de l'utilisateur
- `password` (string) : Mot de passe de l'utilisateur

### Réponse de succès (200 OK)
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "message": "Connexion réussie"
}
```

### Réponse d'erreur (401 Unauthorized)
```json
{
  "error": "Email ou mot de passe incorrect"
}
```

### Réponse d'erreur (400 Bad Request)
```json
{
  "email": ["L'email est requis."],
  "password": ["Le mot de passe est requis."]
}
```

### Codes d'erreur possibles
- `400` : Données invalides
- `401` : Identifiants incorrects
- `500` : Erreur serveur

---

## 🚪 3. Déconnexion (Logout)

### Endpoint
```
POST /api/auth/logout/
```

### Description
Déconnecter l'utilisateur en supprimant son token d'authentification.

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### Body
Aucun body requis.

### Réponse de succès (200 OK)
```json
{
  "message": "Déconnexion réussie"
}
```

### Réponse d'erreur (400 Bad Request)
```json
{
  "error": "Erreur lors de la déconnexion"
}
```

### Codes d'erreur possibles
- `401` : Token invalide ou manquant
- `400` : Erreur lors de la suppression du token
- `500` : Erreur serveur

---

## 👤 4. Profil Utilisateur

### Endpoint
```
GET /api/auth/profile/
```

### Description
Récupérer les informations du profil de l'utilisateur connecté.

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Réponse de succès (200 OK)
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "date_joined": "2024-01-15T10:30:00Z"
}
```

### Codes d'erreur possibles
- `401` : Token invalide ou manquant
- `500` : Erreur serveur

---

## 🔄 5. Renouvellement de Token

### Endpoint
```
POST /api/auth/refresh-token/
```

### Description
Générer un nouveau token d'authentification pour l'utilisateur connecté.

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### Body
Aucun body requis.

### Réponse de succès (200 OK)
```json
{
  "token": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "date_joined": "2024-01-15T10:30:00Z"
  },
  "message": "Token régénéré avec succès"
}
```

### Réponse d'erreur (400 Bad Request)
```json
{
  "error": "Erreur lors de la régénération du token"
}
```

### Codes d'erreur possibles
- `401` : Token invalide ou manquant
- `400` : Erreur lors de la régénération
- `500` : Erreur serveur

---

## 🔒 Gestion des Tokens

### Format du Token
- **Type** : Token d'authentification Django REST Framework
- **Format** : Chaîne de 40 caractères hexadécimaux
- **Durée de vie** : Jusqu'à déconnexion explicite
- **Usage** : Inclus dans le header `Authorization: Token <token>`

### Sécurité
- Les tokens sont uniques par utilisateur
- Un seul token actif par utilisateur à la fois
- Les tokens sont supprimés lors de la déconnexion
- Les tokens sont régénérés lors du refresh

---

## 📝 Exemples d'utilisation

### 1. Inscription d'un nouvel utilisateur
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_smith",
    "email": "jane.smith@example.com",
    "password": "motdepasse123",
    "password_confirm": "motdepasse123",
    "first_name": "Jane",
    "last_name": "Smith"
  }'
```

### 2. Connexion
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@example.com",
    "password": "motdepasse123"
  }'
```

### 3. Récupération du profil
```bash
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

### 4. Déconnexion
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```

---

## ⚠️ Gestion des Erreurs

### Validation des données
- Tous les champs requis doivent être fournis
- L'email doit être au format valide
- Le mot de passe doit contenir au moins 8 caractères
- Les mots de passe doivent correspondre lors de l'inscription
- L'username et l'email doivent être uniques

### Messages d'erreur
- Les erreurs de validation sont retournées avec les champs concernés
- Les erreurs d'authentification sont génériques pour la sécurité
- Les erreurs serveur sont loggées côté backend

---

## 🚀 Intégration Frontend

### Workflow recommandé
1. **Inscription** : Créer un compte avec `/api/auth/register/`
2. **Connexion** : Authentifier avec `/api/auth/login/`
3. **Stockage** : Sauvegarder le token en localStorage/sessionStorage
4. **Utilisation** : Inclure le token dans toutes les requêtes API
5. **Déconnexion** : Supprimer le token avec `/api/auth/logout/`

### Gestion des tokens
```javascript
// Stockage du token
localStorage.setItem('authToken', response.data.token);

// Utilisation du token
const token = localStorage.getItem('authToken');
const headers = {
  'Authorization': `Token ${token}`,
  'Content-Type': 'application/json'
};

// Suppression du token
localStorage.removeItem('authToken');
```

---

## 📊 Codes de Statut HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée avec succès |
| 400 | Bad Request | Données invalides |
| 401 | Unauthorized | Authentification requise/échouée |
| 500 | Internal Server Error | Erreur serveur |

---

## 🔧 Configuration Backend

### Dépendances requises
- Django REST Framework
- Django REST Framework Auth Token
- Django CORS Headers (pour les requêtes cross-origin)

### Settings Django
```python
INSTALLED_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    # ... autres apps
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## ✅ Checklist d'implémentation

- [ ] Endpoint d'inscription fonctionnel
- [ ] Endpoint de connexion fonctionnel
- [ ] Endpoint de déconnexion fonctionnel
- [ ] Endpoint de profil utilisateur fonctionnel
- [ ] Endpoint de renouvellement de token fonctionnel
- [ ] Validation des données côté serveur
- [ ] Gestion des erreurs appropriée
- [ ] Tests unitaires implémentés
- [ ] Documentation API complète
- [ ] Sécurité des tokens assurée

---

**🎉 Votre système d'authentification est maintenant prêt pour l'intégration frontend !**
