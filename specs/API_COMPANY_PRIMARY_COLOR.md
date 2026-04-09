# 🎨 API Company - Primary Color

## 📋 Vue d'ensemble

Le champ `primary_color` permet aux entreprises de personnaliser leur interface avec leur couleur principale. Cette couleur est utilisée pour les éléments d'interface utilisateur comme les boutons, liens, et autres éléments visuels.

---

## 🔧 Détails du champ

### **Champ : `primary_color`**

| Propriété | Valeur |
|-----------|--------|
| **Type** | `string` |
| **Format** | Code couleur hexadécimal |
| **Longueur** | 7 caractères (ex: `#FF5733`) |
| **Valeur par défaut** | `#007bff` (Bleu Bootstrap) |
| **Obligatoire** | Non |
| **Modifiable** | Oui |

### **Format de validation**
- ✅ Format hexadécimal valide : `#RRGGBB`
- ✅ Exemples valides : `#FF5733`, `#2E8B57`, `#DC3545`
- ❌ Exemples invalides : `red`, `#FF`, `#GGGGGG`

---

## 📡 Endpoints concernés

### **1. GET /api/companies/my/**
Récupère la couleur principale de l'entreprise de l'utilisateur connecté.

**Réponse :**
```json
{
  "id": 1,
  "name": "Mon Entreprise SARL",
  "primary_color": "#2E8B57",
  "logo_url": "https://example.com/logo.png",
  "email": "contact@monentreprise.com",
  // ... autres champs
}
```

### **2. GET /api/companies/{id}/**
Récupère la couleur principale d'une entreprise spécifique (Super Admin uniquement).

**Réponse :**
```json
{
  "id": 2,
  "name": "Autre Entreprise",
  "primary_color": "#FF6B35",
  "logo_url": "https://example.com/logo2.png",
  "email": "contact@autre.com",
  // ... autres champs
}
```

### **3. GET /api/companies/**
Liste toutes les entreprises avec leurs couleurs (Super Admin uniquement).

**Réponse :**
```json
[
  {
    "id": 1,
    "name": "Entreprise A",
    "primary_color": "#2E8B57",
    "logo_url": "https://example.com/logo1.png",
    "email": "contact@a.com"
  },
  {
    "id": 2,
    "name": "Entreprise B", 
    "primary_color": "#FF6B35",
    "logo_url": "https://example.com/logo2.png",
    "email": "contact@b.com"
  }
]
```

---

## 🎨 Utilisation Frontend

### **CSS Variables**
```css
:root {
  --company-primary-color: #2E8B57;
  --company-primary-hover: #228B22;
  --company-primary-light: #90EE90;
}
```

### **JavaScript - Récupération de la couleur**
```javascript
const getCompanyColor = async (token) => {
  try {
    const response = await fetch('/api/companies/my/', {
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) throw new Error('Erreur API');
    
    const company = await response.json();
    return company.primary_color;
  } catch (error) {
    console.error('Erreur:', error);
    return '#007bff'; // Couleur par défaut
  }
};
```

### **React Hook - Gestion de la couleur**
```javascript
import { useState, useEffect } from 'react';

const useCompanyColor = (token) => {
  const [primaryColor, setPrimaryColor] = useState('#007bff');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchColor = async () => {
      try {
        const response = await fetch('/api/companies/my/', {
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.ok) {
          const company = await response.json();
          setPrimaryColor(company.primary_color);
        }
      } catch (error) {
        console.error('Erreur lors du chargement de la couleur:', error);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchColor();
    }
  }, [token]);

  return { primaryColor, loading };
};

export default useCompanyColor;
```

### **Vue.js - Composable**
```javascript
import { ref, onMounted } from 'vue';

export const useCompanyColor = (token) => {
  const primaryColor = ref('#007bff');
  const loading = ref(true);

  const fetchColor = async () => {
    try {
      const response = await fetch('/api/companies/my/', {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const company = await response.json();
        primaryColor.value = company.primary_color;
      }
    } catch (error) {
      console.error('Erreur lors du chargement de la couleur:', error);
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    if (token) {
      fetchColor();
    }
  });

  return { primaryColor, loading };
};
```

---

## 🎯 Exemples d'utilisation

### **1. Boutons personnalisés**
```css
.btn-primary {
  background-color: var(--company-primary-color);
  border-color: var(--company-primary-color);
}

.btn-primary:hover {
  background-color: var(--company-primary-hover);
  border-color: var(--company-primary-hover);
}
```

### **2. Liens personnalisés**
```css
a {
  color: var(--company-primary-color);
}

a:hover {
  color: var(--company-primary-hover);
}
```

### **3. Indicateurs de statut**
```css
.status-active {
  color: var(--company-primary-color);
  background-color: var(--company-primary-light);
}
```

---

## 🔄 Mise à jour en temps réel

### **WebSocket (optionnel)**
```javascript
// Écouter les changements de couleur en temps réel
const ws = new WebSocket('ws://localhost:8000/ws/company/');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'color_updated') {
    document.documentElement.style.setProperty('--company-primary-color', data.color);
  }
};
```

---

## ⚠️ Notes importantes

1. **Fallback** : Toujours prévoir une couleur par défaut en cas d'erreur
2. **Performance** : Mettre en cache la couleur pour éviter les requêtes répétées
3. **Accessibilité** : Vérifier le contraste avec les couleurs de fond
4. **Validation** : Valider le format hexadécimal côté frontend
5. **Thème sombre** : Adapter la couleur selon le thème de l'utilisateur

---

## 🧪 Tests

### **Test de récupération**
```javascript
// Test unitaire
test('should fetch company primary color', async () => {
  const mockResponse = { primary_color: '#2E8B57' };
  jest.spyOn(global, 'fetch').mockResolvedValue({
    ok: true,
    json: () => Promise.resolve(mockResponse)
  });

  const color = await getCompanyColor('fake-token');
  expect(color).toBe('#2E8B57');
});
```

### **Test d'application CSS**
```javascript
// Test d'intégration
test('should apply company color to CSS variables', () => {
  const color = '#2E8B57';
  document.documentElement.style.setProperty('--company-primary-color', color);
  
  const computedStyle = getComputedStyle(document.documentElement);
  expect(computedStyle.getPropertyValue('--company-primary-color')).toBe(color);
});
```

---

## 📚 Ressources

- [Couleurs hexadécimales](https://www.w3schools.com/colors/colors_hexadecimal.asp)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [Contraste des couleurs](https://webaim.org/resources/contrastchecker/)

---

**✅ Le champ `primary_color` est maintenant disponible dans toutes les APIs Company !**
