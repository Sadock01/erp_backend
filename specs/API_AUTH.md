# API Authentification - Documentation

## Endpoints d'authentification

### Base URL
```
/api/auth/
```

## 1. **POST /api/auth/login/**
- **Description** : Connexion d'un utilisateur avec email et génération d'un token
- **Permissions** : Aucune (AllowAny)
- **Body** :
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```
- **Réponse** :
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "message": "Connexion réussie"
}
```

## 2. **POST /api/auth/logout/**
- **Description** : Déconnexion d'un utilisateur (suppression du token)
- **Permissions** : Authentifié
- **Headers** : `Authorization: Token YOUR_TOKEN`
- **Réponse** :
```json
{
  "message": "Déconnexion réussie"
}
```

## 3. **GET /api/auth/profile/**
- **Description** : Récupérer le profil de l'utilisateur connecté
- **Permissions** : Authentifié
- **Headers** : `Authorization: Token YOUR_TOKEN`
- **Réponse** :
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "first_name": "",
  "last_name": "",
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

## 4. **POST /api/auth/refresh-token/**
- **Description** : Régénérer un nouveau token
- **Permissions** : Authentifié
- **Headers** : `Authorization: Token YOUR_TOKEN`
- **Réponse** :
```json
{
  "token": "nouveau_token_ici",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "message": "Token régénéré avec succès"
}
```

## Exemples d'utilisation Postman

### 1. Connexion
```
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "admin123"
}
```

### 2. Utiliser le token pour accéder aux APIs
```
GET http://localhost:8000/api/customers/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### 3. Déconnexion
```
POST http://localhost:8000/api/auth/logout/
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

## Codes de réponse

- **200** : Succès
- **400** : Erreur de validation
- **401** : Non authentifié / Identifiants incorrects
- **500** : Erreur serveur

## Workflow complet

1. **Créer un superutilisateur** : `python manage.py createsuperuser` (avec un email valide)
2. **Se connecter** : `POST /api/auth/login/` avec email/password
3. **Récupérer le token** de la réponse
4. **Utiliser le token** dans toutes les requêtes API
5. **Se déconnecter** : `POST /api/auth/logout/`
