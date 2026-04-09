# 🏢 API Get My Company - Frontend Documentation

## 📋 Vue d'ensemble

Cette API permet de récupérer les informations de l'entreprise de l'utilisateur connecté. Elle est utilisée pour afficher les données de l'entreprise dans le dashboard et les formulaires.

---

## 🌐 Base URL

```
http://localhost:8000/api/
```

---

## 🏢 Get My Company

### Endpoint
```
GET /api/companies/my/
```

### Description
Récupérer les informations complètes de l'entreprise de l'utilisateur connecté.

### Authentification
- **Requis** : Token d'authentification dans le header `Authorization`
- **Format** : `Token YOUR_TOKEN_HERE`

### Headers
```
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
Content-Type: application/json
```

### Paramètres
Aucun paramètre requis.

---

## ✅ Réponse de succès (200 OK)

### Structure de la réponse
```json
{
  "id": 1,
  "name": "Mon Entreprise SARL",
  "logo": null,
  "logo_url": null,
  "primary_color": "#2E8B57",
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

### Description des champs

| Champ | Type | Description |
|-------|------|-------------|
| `id` | integer | ID unique de l'entreprise |
| `name` | string | Nom de l'entreprise |
| `logo` | string/null | Chemin du logo (peut être null) |
| `logo_url` | string/null | URL complète du logo (peut être null) |
| `primary_color` | string | Couleur principale de l'entreprise (hexadécimal) |
| `description` | string | Description de l'entreprise |
| `email` | string | Email de contact principal |
| `phone` | string | Numéro de téléphone |
| `address` | string | Adresse complète |
| `city` | string | Ville |
| `postal_code` | string | Code postal |
| `country` | string | Pays |
| `website` | string | Site web de l'entreprise |
| `tax_number` | string | Numéro de TVA |
| `registration_number` | string | Numéro d'enregistrement (SIRET) |
| `is_active` | boolean | Statut actif de l'entreprise |
| `settings` | object | Paramètres personnalisés (JSON) |
| `user_count` | integer | Nombre d'utilisateurs dans l'entreprise |
| `admin_count` | integer | Nombre d'admins dans l'entreprise |
| `full_address` | string | Adresse complète formatée |
| `created_at` | datetime | Date de création (ISO 8601) |
| `updated_at` | datetime | Date de dernière modification (ISO 8601) |

---

## ❌ Réponses d'erreur

### 401 Unauthorized
```json
{
  "error": "Authentification requise",
  "detail": "Vous devez être connecté pour accéder à cette ressource"
}
```

### 404 Not Found
```json
{
  "error": "Profil non trouvé",
  "detail": "Vous n'êtes associé à aucune entreprise"
}
```

### 500 Internal Server Error
```json
{
  "error": "Erreur serveur",
  "detail": "Une erreur interne s'est produite"
}
```

---

## 🧪 Exemples d'utilisation

### JavaScript (Fetch)
```javascript
const getMyCompany = async (token) => {
  try {
    const response = await fetch('http://localhost:8000/api/companies/my/', {
      method: 'GET',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Erreur lors de la récupération de l\'entreprise');
    }

    const company = await response.json();
    return company;
  } catch (error) {
    console.error('Erreur:', error.message);
    throw error;
  }
};

// Utilisation
getMyCompany('YOUR_TOKEN_HERE')
  .then(company => {
    console.log('Entreprise:', company);
    // Utiliser les données de l'entreprise
  })
  .catch(error => {
    console.error('Erreur:', error);
  });
```

### Axios
```javascript
import axios from 'axios';

const getMyCompany = async (token) => {
  try {
    const response = await axios.get('http://localhost:8000/api/companies/my/', {
      headers: {
        'Authorization': `Token ${token}`
      }
    });
    return response.data;
  } catch (error) {
    if (error.response) {
      throw new Error(error.response.data.detail || 'Erreur API');
    }
    throw error;
  }
};
```

### React Hook
```javascript
import { useState, useEffect } from 'react';

const useMyCompany = (token) => {
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCompany = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/companies/my/', {
          headers: {
            'Authorization': `Token ${token}`
          }
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Erreur lors de la récupération');
        }

        const companyData = await response.json();
        setCompany(companyData);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchCompany();
    }
  }, [token]);

  return { company, loading, error };
};
```

---

## 📝 Notes importantes

### Authentification
- **Token requis** : L'utilisateur doit être authentifié
- **Format du token** : `Token YOUR_TOKEN_HERE` dans le header Authorization
- **Expiration** : Le token peut expirer, gérer les erreurs 401

### Gestion des erreurs
- **401** : Rediriger vers la page de connexion
- **404** : L'utilisateur n'est associé à aucune entreprise (cas rare)
- **500** : Afficher un message d'erreur générique

### Données utiles pour l'UI
- **`logo_url`** : Pour afficher le logo de l'entreprise
- **`full_address`** : Adresse formatée prête à afficher
- **`user_count`** et **`admin_count`** : Pour les statistiques
- **`settings`** : Paramètres personnalisés de l'entreprise

### Performance
- **Cache** : Considérer mettre en cache les données de l'entreprise
- **Refresh** : Rafraîchir les données si l'utilisateur modifie son profil

---

## 🔄 Cas d'usage typiques

1. **Dashboard** : Afficher le nom et le logo de l'entreprise
2. **Profil utilisateur** : Montrer l'entreprise de l'utilisateur
3. **Paramètres** : Pré-remplir les formulaires avec les données de l'entreprise
4. **Statistiques** : Afficher le nombre d'utilisateurs et d'admins
5. **Informations de contact** : Afficher les coordonnées de l'entreprise
