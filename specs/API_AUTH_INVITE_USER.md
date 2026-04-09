# 👥 Spécifications API Invitation d'Utilisateur - Baobab ERP

## 📋 Vue d'ensemble

Cette documentation décrit l'API d'invitation d'utilisateurs pour l'ERP Baobab. Cette API permet aux administrateurs d'inviter de nouveaux utilisateurs à rejoindre leur entreprise.

---

## 🌐 Base URL

```
http://localhost:8000/api/
```

---

## 👥 Invitation d'Utilisateur

### Endpoint
```
POST /api/auth/invite-user/
```

### Description
Inviter un nouvel utilisateur à rejoindre une entreprise existante. L'utilisateur reçoit un mot de passe temporaire par email et doit le changer lors de sa première connexion.

### Authentification
- **Requis** : Token d'authentification
- **Permission** : `users_manage`

### Headers
```
Content-Type: application/json
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Body (JSON)
```json
{
  "email": "nouvel.utilisateur@entreprise.com",
  "first_name": "Jean",
  "last_name": "Dupont",
  "role": "Sales",
  "company_id": 1,
  "send_email": true
}
```

### Champs requis
- `email` (string, format email) : Email de l'utilisateur à inviter
- `first_name` (string, max 30 caractères) : Prénom de l'utilisateur
- `last_name` (string, max 30 caractères) : Nom de famille de l'utilisateur
- `role` (string) : Rôle à attribuer à l'utilisateur
- `company_id` (integer) : ID de l'entreprise

### Champs optionnels
- `send_email` (boolean) : Envoyer l'email d'invitation (défaut: true)

### Rôles disponibles
- `Admin` : Administrateur avec toutes les permissions
- `Super Admin` : Accès complet au système
- `Manager` : Gestionnaire avec accès aux rapports
- `Sales` : Commercial
- `Stock Manager` : Gestionnaire de stock
- `Viewer` : Consultation seule

### Réponse de succès (201 Created)
```json
{
  "message": "Utilisateur invité avec succès et email d'invitation envoyé",
  "user": {
    "id": 2,
    "username": "nouvel.utilisateur@entreprise.com",
    "email": "nouvel.utilisateur@entreprise.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "is_active": true
  },
  "company": {
    "id": 1,
    "name": "Mon Entreprise SARL"
  },
  "role": "Sales",
  "email_sent": true,
  "temp_password": null
}
```

### Réponse avec email non envoyé
```json
{
  "message": "Utilisateur invité avec succès (email non envoyé)",
  "user": {
    "id": 2,
    "username": "nouvel.utilisateur@entreprise.com",
    "email": "nouvel.utilisateur@entreprise.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "is_active": true
  },
  "company": {
    "id": 1,
    "name": "Mon Entreprise SARL"
  },
  "role": "Sales",
  "email_sent": false,
  "temp_password": "Abc123Xyz789"
}
```

### Réponse d'erreur (400 Bad Request)

#### Erreurs de validation
```json
{
  "email": ["Un utilisateur avec cet email existe déjà."],
  "role": ["Le rôle 'InvalidRole' n'existe pas ou n'est pas actif."],
  "company_id": ["L'entreprise avec l'ID 999 n'existe pas ou n'est pas active."]
}
```

### Réponse d'erreur (403 Forbidden)
```json
{
  "error": "Permission refusée",
  "detail": "Vous n'avez pas la permission d'inviter des utilisateurs",
  "required_permission": "users_manage"
}
```

### Codes d'erreur possibles
- `400` : Données invalides, utilisateur déjà existant, rôle ou entreprise invalide
- `401` : Non authentifié
- `403` : Permission refusée
- `500` : Erreur serveur

---

## 📧 Email d'invitation

### Contenu de l'email
L'utilisateur reçoit un email avec :
- **Sujet** : "Invitation à rejoindre [Nom de l'entreprise] sur Baobab ERP"
- **Contenu** :
  - Salutation personnalisée
  - Nom de l'entreprise
  - Nom de la personne qui invite
  - Identifiants temporaires (email + mot de passe)
  - Lien de connexion
  - Instructions pour changer le mot de passe

### Exemple d'email
```
Sujet: Invitation à rejoindre Mon Entreprise SARL sur Baobab ERP

Bonjour Jean Dupont,

Vous avez été invité(e) par John Doe à rejoindre l'entreprise "Mon Entreprise SARL" sur Baobab ERP.

Vos identifiants de connexion temporaires :
- Email : nouvel.utilisateur@entreprise.com
- Mot de passe temporaire : Abc123Xyz789

IMPORTANT : Vous devrez changer ce mot de passe lors de votre première connexion.

Pour vous connecter, rendez-vous sur : http://localhost:3000/login

Cordialement,
L'équipe Baobab ERP
```

---

## 🔄 Processus d'invitation

1. **Validation** : Vérification des permissions et des données
2. **Création utilisateur** : Création du compte avec mot de passe temporaire
3. **Attribution rôle** : Attribution du rôle spécifié
4. **Envoi email** : Envoi de l'email d'invitation (si demandé)
5. **Réponse** : Retour des informations de l'utilisateur créé

---

## 🧪 Exemples de test

### Test avec envoi d'email
```bash
curl -X POST http://localhost:8000/api/auth/invite-user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "email": "nouvel.utilisateur@entreprise.com",
    "first_name": "Jean",
    "last_name": "Dupont",
    "role": "Sales",
    "company_id": 1,
    "send_email": true
  }'
```

### Test sans envoi d'email
```bash
curl -X POST http://localhost:8000/api/auth/invite-user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "email": "test.user@entreprise.com",
    "first_name": "Test",
    "last_name": "User",
    "role": "Viewer",
    "company_id": 1,
    "send_email": false
  }'
```

### Test avec différents rôles
```bash
# Inviter un Manager
curl -X POST http://localhost:8000/api/auth/invite-user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "email": "manager@entreprise.com",
    "first_name": "Marie",
    "last_name": "Manager",
    "role": "Manager",
    "company_id": 1
  }'

# Inviter un Stock Manager
curl -X POST http://localhost:8000/api/auth/invite-user/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -d '{
    "email": "stock@entreprise.com",
    "first_name": "Pierre",
    "last_name": "Stock",
    "role": "Stock Manager",
    "company_id": 1
  }'
```

---

## 📝 Notes importantes

- **Mot de passe temporaire** : Généré automatiquement (12 caractères alphanumériques)
- **Username** : Utilise l'email comme nom d'utilisateur
- **Première connexion** : L'utilisateur doit changer son mot de passe
- **Permissions** : Seuls les utilisateurs avec la permission `users_manage` peuvent inviter
- **Entreprise** : L'utilisateur est automatiquement lié à l'entreprise spécifiée
- **Rôle** : Le rôle doit exister et être actif dans le système

---

## 🔐 Sécurité

- **Authentification requise** : Seuls les utilisateurs authentifiés peuvent inviter
- **Permissions** : Vérification de la permission `users_manage`
- **Validation** : Validation stricte de tous les champs
- **Email unique** : Un utilisateur ne peut pas être créé avec un email existant
- **Mot de passe sécurisé** : Génération aléatoire avec `secrets` module
