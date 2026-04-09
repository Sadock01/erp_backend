# 🔐 Spécifications API Inscription avec Entreprise - Baobab ERP

## 📋 Vue d'ensemble

Cette documentation décrit l'API d'inscription mise à jour pour l'ERP Baobab, qui crée automatiquement un utilisateur ET son entreprise lors de l'inscription.

---

## 🌐 Base URL

```
http://localhost:8000/api/
```

---

## 🔑 Inscription avec Création d'Entreprise (Register)

### Endpoint
```
POST /api/auth/register/
```

### Description
Créer un nouveau compte utilisateur dans le système avec création automatique de son entreprise. L'utilisateur reçoit automatiquement le rôle Admin.

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
  "last_name": "Doe",
  "company_name": "Mon Entreprise SARL",
  "company_phone": "01 23 45 67 89",
  "company_address": "123 Rue de la Paix",
  "company_city": "Paris",
  "company_postal_code": "75001",
  "company_country": "France",
  "company_description": "Ma belle entreprise de vente en ligne",
  "company_website": "https://monentreprise.com",
  "company_tax_number": "FR12345678901",
  "company_registration_number": "12345678901234"
}
```

### Champs Utilisateur

#### Champs requis
- `username` (string, max 150 caractères) : Nom d'utilisateur unique
- `email` (string, format email) : Adresse email unique
- `password` (string, min 8 caractères) : Mot de passe
- `password_confirm` (string) : Confirmation du mot de passe

#### Champs optionnels
- `first_name` (string, max 30 caractères) : Prénom
- `last_name` (string, max 30 caractères) : Nom de famille

### Champs Entreprise

#### Champs requis
- `company_name` (string, max 200 caractères) : Nom officiel de l'entreprise
- `company_phone` (string, max 20 caractères) : Numéro de téléphone principal
- `company_city` (string, max 100 caractères) : Ville de l'entreprise

#### Champs optionnels
- `company_address` (string) : Adresse complète de l'entreprise
- `company_description` (string) : Description de l'entreprise
- `company_postal_code` (string, max 10 caractères) : Code postal
- `company_country` (string, max 100 caractères) : Pays (défaut: "France")
- `company_website` (string, format URL) : Site web de l'entreprise
- `company_tax_number` (string, max 50 caractères) : Numéro de TVA intracommunautaire
- `company_registration_number` (string, max 50 caractères) : Numéro SIRET ou équivalent
- `company_logo` (file, format image) : Logo de l'entreprise (JPG, PNG, GIF, etc.)
- `company_primary_color` (string, max 7 caractères) : Couleur principale de l'entreprise (format hexadécimal, ex: #007bff). Par défaut: #007bff

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
  "company": {
    "id": 1,
    "name": "Mon Entreprise SARL",
    "email": "john.doe@example.com",
    "description": "Ma belle entreprise de vente en ligne",
    "phone": "01 23 45 67 89",
    "address": "123 Rue de la Paix",
    "city": "Paris",
    "postal_code": "75001",
    "country": "France",
    "website": "https://monentreprise.com",
    "tax_number": "FR12345678901",
    "registration_number": "12345678901234",
    "logo": "http://localhost:8000/media/companies/logos/logo_entreprise.jpg",
    "primary_color": "#007bff",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "message": "Inscription réussie, entreprise créée et rôle Admin attribué"
}
```

### Réponse d'erreur (400 Bad Request)

#### Erreurs de validation utilisateur
```json
{
  "username": ["Ce nom d'utilisateur est déjà utilisé."],
  "email": ["Cet email est déjà utilisé."],
  "password": ["Ce champ est requis."],
  "password_confirm": ["Les mots de passe ne correspondent pas."]
}
```

#### Erreurs de validation entreprise
```json
{
  "company_name": ["Ce champ est requis."],
  "company_phone": ["Le champ phone de l'entreprise est requis."],
  "company_city": ["Le champ city de l'entreprise est requis."]
}
```

#### Erreurs de validation URL
```json
{
  "company_website": ["Entrez une URL valide."]
}
```

### Codes d'erreur possibles
- `400` : Données invalides, utilisateur déjà existant, champs entreprise manquants, ou format d'image invalide
- `500` : Erreur serveur

### Formats d'image supportés
- **JPG/JPEG** : Format recommandé pour les photos
- **PNG** : Format recommandé pour les logos avec transparence
- **GIF** : Format supporté
- **Taille maximale** : 5MB (configurable)
- **Résolution recommandée** : 200x200px minimum, 800x800px maximum

---

## 🔄 Processus d'inscription

1. **Validation des données** : Vérification de tous les champs requis
2. **Création de l'utilisateur** : Création du compte utilisateur avec les informations fournies
3. **Création de l'entreprise** : Création automatique de l'entreprise avec les informations fournies
4. **Attribution du rôle** : Attribution automatique du rôle "Admin" à l'utilisateur
5. **Génération du token** : Création d'un token d'authentification
6. **Réponse** : Retour des informations utilisateur, entreprise et token

---

## 📝 Notes importantes

- L'email de l'utilisateur est automatiquement utilisé comme email de contact de l'entreprise
- L'utilisateur reçoit automatiquement le rôle "Admin" lors de l'inscription
- Tous les champs entreprise requis doivent être remplis
- Le pays par défaut est "France" si non spécifié
- L'entreprise est créée avec le statut "active" par défaut

---

## 🧪 Exemples de test

### Test avec données minimales
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "company_name": "Test Company",
    "company_phone": "01 23 45 67 89",
    "company_address": "123 Test Street",
    "company_city": "Paris"
  }'
```

### Test avec données complètes (sans image)
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john.doe@example.com",
    "password": "motdepasse123",
    "password_confirm": "motdepasse123",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Mon Entreprise SARL",
    "company_phone": "01 23 45 67 89",
    "company_address": "123 Rue de la Paix",
    "company_city": "Paris",
    "company_postal_code": "75001",
    "company_country": "France",
    "company_description": "Ma belle entreprise de vente en ligne",
    "company_website": "https://monentreprise.com",
    "company_tax_number": "FR12345678901",
    "company_registration_number": "12345678901234"
  }'
```

### Test avec upload d'image
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -F "username=john_doe" \
  -F "email=john.doe@example.com" \
  -F "password=motdepasse123" \
  -F "password_confirm=motdepasse123" \
  -F "first_name=John" \
  -F "last_name=Doe" \
  -F "company_name=Mon Entreprise SARL" \
  -F "company_phone=01 23 45 67 89" \
  -F "company_address=123 Rue de la Paix" \
  -F "company_city=Paris" \
  -F "company_postal_code=75001" \
  -F "company_country=France" \
  -F "company_description=Ma belle entreprise de vente en ligne" \
  -F "company_website=https://monentreprise.com" \
  -F "company_tax_number=FR12345678901" \
  -F "company_registration_number=12345678901234" \
  -F "company_logo=@/path/to/logo.png"
```

### Test avec données minimales + image
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -F "username=test_user" \
  -F "email=test@example.com" \
  -F "password=password123" \
  -F "password_confirm=password123" \
  -F "company_name=Test Company" \
  -F "company_phone=01 23 45 67 89" \
  -F "company_address=123 Test Street" \
  -F "company_city=Paris" \
  -F "company_logo=@/path/to/logo.jpg"
```
