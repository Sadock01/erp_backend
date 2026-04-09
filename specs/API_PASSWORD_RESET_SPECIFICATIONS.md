# API Password Reset - Spécifications Frontend

## Vue d'ensemble

Les APIs de reset de mot de passe permettent aux utilisateurs de réinitialiser leur mot de passe en utilisant un code de vérification envoyé par email.

## Endpoints

### 1. Demande de Reset de Mot de Passe

**Endpoint:** `POST /api/auth/password-reset-request/`

**Description:** Demande un code de vérification pour réinitialiser le mot de passe.

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
    "email": "user@example.com"
}
```

**Réponse de Succès (200):**
```json
{
    "message": "Code de vérification envoyé par email",
    "email": "user@example.com",
    "expires_in": 15
}
```

**Réponse d'Erreur (400):**
```json
{
    "email": ["Ce champ est requis."]
}
```

**Réponse d'Erreur (400) - Email invalide:**
```json
{
    "email": ["Saisissez une adresse email valide."]
}
```

**Notes:**
- Le code est affiché dans le terminal du serveur (simulation d'email)
- Le code expire dans 15 minutes
- Pour la sécurité, la réponse est identique même si l'email n'existe pas
- L'utilisateur doit vérifier le terminal du serveur pour obtenir le code

---

### 2. Confirmation du Reset de Mot de Passe

**Endpoint:** `POST /api/auth/password-reset-confirm/`

**Description:** Confirme le reset de mot de passe avec le code de vérification.

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
    "email": "user@example.com",
    "code": "123456",
    "new_password": "nouveau_mot_de_passe",
    "new_password_confirm": "nouveau_mot_de_passe"
}
```

**Réponse de Succès (200):**
```json
{
    "message": "Mot de passe réinitialisé avec succès",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "user@example.com"
    }
}
```

**Réponses d'Erreur (400):**

Code incorrect:
```json
{
    "error": "Code incorrect"
}
```

Code invalide/expiré:
```json
{
    "error": "Code invalide, expiré ou déjà utilisé"
}
```

Code de vérification invalide:
```json
{
    "error": "Code de vérification invalide"
}
```

Validation des données:
```json
{
    "email": ["Ce champ est requis."],
    "code": ["Ce champ est requis."],
    "new_password": ["Ce champ est requis."],
    "new_password_confirm": ["Ce champ est requis."]
}
```

Mots de passe différents:
```json
{
    "non_field_errors": ["Les nouveaux mots de passe ne correspondent pas."]
}
```

**Notes:**
- Le code doit être exactement celui affiché dans le terminal
- Le code ne peut être utilisé qu'une seule fois
- Maximum 3 tentatives par code
- Tous les tokens existants de l'utilisateur sont supprimés après le reset

---

## Processus de Reset

### Étape 1: Demande de Reset
1. L'utilisateur saisit son email
2. Envoi de la requête `POST /api/auth/password-reset-request/`
3. Un code de 6 chiffres est généré et affiché dans le terminal du serveur
4. Les anciens codes pour cet email sont désactivés

### Étape 2: Validation du Code
1. L'utilisateur saisit l'email, le code et le nouveau mot de passe
2. Envoi de la requête `POST /api/auth/password-reset-confirm/`
3. Le système vérifie la validité du code
4. Le mot de passe est mis à jour
5. Le code est marqué comme utilisé
6. Tous les tokens de l'utilisateur sont supprimés

---

## Exemples d'Utilisation Frontend

### 1. Demande de Reset

```javascript
// Fonction pour demander un reset
async function requestPasswordReset(email) {
    try {
        const response = await fetch('/api/auth/password-reset-request/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Succès - afficher message et demander le code
            console.log('Code envoyé:', data.message);
            console.log('Vérifiez le terminal du serveur pour le code');
            return { success: true, data };
        } else {
            // Erreur de validation
            console.error('Erreur:', data);
            return { success: false, errors: data };
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        return { success: false, error: 'Erreur de connexion' };
    }
}
```

### 2. Confirmation du Reset

```javascript
// Fonction pour confirmer le reset
async function confirmPasswordReset(email, code, newPassword, confirmPassword) {
    try {
        const response = await fetch('/api/auth/password-reset-confirm/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email,
                code,
                new_password: newPassword,
                new_password_confirm: confirmPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Succès - rediriger vers login
            console.log('Mot de passe réinitialisé:', data.message);
            return { success: true, data };
        } else {
            // Erreur
            console.error('Erreur:', data);
            return { success: false, error: data.error || data };
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        return { success: false, error: 'Erreur de connexion' };
    }
}
```

### 3. Interface Utilisateur Complète

```javascript
// Exemple d'interface complète
class PasswordResetForm {
    constructor() {
        this.step = 1; // 1: email, 2: code + password
        this.email = '';
    }
    
    async handleEmailSubmit(email) {
        this.email = email;
        const result = await requestPasswordReset(email);
        
        if (result.success) {
            this.step = 2;
            this.showCodeForm();
        } else {
            this.showError(result.errors);
        }
    }
    
    async handleCodeSubmit(code, newPassword, confirmPassword) {
        const result = await confirmPasswordReset(
            this.email, 
            code, 
            newPassword, 
            confirmPassword
        );
        
        if (result.success) {
            this.showSuccess();
            // Rediriger vers la page de login
            window.location.href = '/login';
        } else {
            this.showError(result.error);
        }
    }
    
    showCodeForm() {
        // Afficher le formulaire de saisie du code
        document.getElementById('email-step').style.display = 'none';
        document.getElementById('code-step').style.display = 'block';
    }
    
    showError(error) {
        // Afficher l'erreur à l'utilisateur
        console.error('Erreur:', error);
    }
    
    showSuccess() {
        // Afficher le message de succès
        console.log('Mot de passe réinitialisé avec succès!');
    }
}
```

---

## Codes d'Erreur

| Code HTTP | Description | Action Frontend |
|-----------|-------------|-----------------|
| 200 | Succès | Afficher le message de succès |
| 400 | Données invalides | Afficher les erreurs de validation |
| 500 | Erreur serveur | Afficher un message d'erreur générique |

---

## Messages d'Erreur Spécifiques

### Demande de Reset
- `"Ce champ est requis."` - Email manquant
- `"Saisissez une adresse email valide."` - Format email invalide

### Confirmation de Reset
- `"Code incorrect"` - Code saisi incorrect
- `"Code invalide, expiré ou déjà utilisé"` - Code expiré ou déjà utilisé
- `"Code de vérification invalide"` - Code inexistant
- `"Les nouveaux mots de passe ne correspondent pas."` - Mots de passe différents
- `"Ce champ est requis."` - Champ manquant

---

## Sécurité

- **Codes à usage unique:** Chaque code ne peut être utilisé qu'une seule fois
- **Expiration:** Les codes expirent après 15 minutes
- **Limite de tentatives:** Maximum 3 tentatives par code
- **Suppression des tokens:** Tous les tokens existants sont supprimés après reset
- **Pas de révélation d'email:** La réponse est identique même si l'email n'existe pas

---

## Interface Utilisateur Recommandée

### Étape 1: Saisie de l'Email
```html
<form id="email-step">
    <h2>Réinitialiser le mot de passe</h2>
    <p>Entrez votre adresse email pour recevoir un code de vérification.</p>
    
    <div class="form-group">
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required>
        <div class="error-message" id="email-error"></div>
    </div>
    
    <button type="submit">Envoyer le code</button>
</form>
```

### Étape 2: Saisie du Code et Nouveau Mot de Passe
```html
<form id="code-step" style="display: none;">
    <h2>Code de vérification</h2>
    <p>Entrez le code reçu et votre nouveau mot de passe.</p>
    <p class="info">Vérifiez le terminal du serveur pour obtenir le code.</p>
    
    <div class="form-group">
        <label for="code">Code de vérification</label>
        <input type="text" id="code" name="code" maxlength="6" required>
        <div class="error-message" id="code-error"></div>
    </div>
    
    <div class="form-group">
        <label for="new-password">Nouveau mot de passe</label>
        <input type="password" id="new-password" name="new_password" required>
        <div class="error-message" id="password-error"></div>
    </div>
    
    <div class="form-group">
        <label for="confirm-password">Confirmer le mot de passe</label>
        <input type="password" id="confirm-password" name="confirm_password" required>
        <div class="error-message" id="confirm-error"></div>
    </div>
    
    <button type="submit">Réinitialiser le mot de passe</button>
</form>
```

---

## Test des APIs

### 1. Test avec cURL

**Demande de reset:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset-request/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

**Confirmation du reset:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset-confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "code": "123456",
    "new_password": "nouveau_mot_de_passe",
    "new_password_confirm": "nouveau_mot_de_passe"
  }'
```

### 2. Test avec JavaScript

```javascript
// Test complet
async function testPasswordReset() {
    // 1. Demande de reset
    const resetResult = await requestPasswordReset('test@example.com');
    console.log('Reset request:', resetResult);
    
    // 2. Attendre que l'utilisateur entre le code
    const code = prompt('Entrez le code affiché dans le terminal:');
    
    // 3. Confirmation
    const confirmResult = await confirmPasswordReset(
        'test@example.com',
        code,
        'nouveau_mot_de_passe',
        'nouveau_mot_de_passe'
    );
    console.log('Reset confirm:', confirmResult);
}
```

---

## Notes Importantes

1. **Code dans le terminal:** Le code de vérification est affiché dans le terminal du serveur Django, pas envoyé par email
2. **Expiration:** Le code expire après 15 minutes
3. **Tentatives limitées:** Maximum 3 tentatives par code
4. **Sécurité:** Tous les tokens existants sont supprimés après reset
5. **Validation:** Les mots de passe doivent correspondre et respecter les règles de validation