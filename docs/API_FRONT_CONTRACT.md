# Contrat d’intégration Front (Next.js) ↔ Backend (Django DRF) — Nodus ERP

**But** : permettre au frontend d’implémenter l’intégration API **sans ambiguïté**, d’abord **en local**, puis sur staging/production.

Ce document reflète **les routes et formats réellement implémentés dans le repo**.

---

## 0) Base URL & préfixes

- **Local** : `http://127.0.0.1:8000`
- **Préfixe API** : `/api`
- Exemple : `GET http://127.0.0.1:8000/api/auth/profile/`

---

## 1) Authentification (DRF Token)

### 1.1 Login
- **POST** `/api/auth/login/`
- **Body** :

```json
{ "email": "user@example.com", "password": "string" }
```

- **Réponse 200 (exemple)** :

```json
{
  "token": "…",
  "user": {
    "id": 16,
    "username": "admin_nodus",
    "email": "admin@nodus.local",
    "first_name": "",
    "last_name": "",
    "is_active": true,
    "date_joined": "2026-04-08T17:14:03.336050+02:00"
  },
  "message": "Connexion réussie"
}
```

### 1.2 Header à envoyer sur les endpoints protégés
Le backend utilise le schéma **DRF Token** (pas `Bearer`) :

```
Authorization: Token <token>
```

### 1.3 Utilisateur courant
- **GET** `/api/auth/profile/` — lecture du user courant
- **PATCH** ou **PUT** `/api/auth/profile/` — mise à jour **self-service** (voir **§1.8**)
- **Réponse** : objet user (sans enveloppe `success/data`)

### 1.4 Logout
- **POST** `/api/auth/logout/`

### 1.5 Refresh token
- **POST** `/api/auth/refresh-token/`
> À valider côté front selon le comportement attendu (durée, invalidation, etc.).

### 1.6 Entreprise courante — pourquoi le front voit « l’identifiant de la company manque »

**Cause fréquente** : la réponse de **`POST /api/auth/login/`** contient `token` et `user`, mais **pas** de champ `company_id`. Si l’UI ou un formulaire (ex. invitation membre) exige un `company_id` sans l’avoir chargé ailleurs, tu obtiens un message du type *« l’identifiant de la company manque »* **côté front** (validation locale) ou une erreur API **`company_id`: champ requis** sur les endpoints qui le demandent explicitement dans le JSON.

**Ce que le backend attend**

| Besoin | Ce qu’il faut faire côté front |
|--------|--------------------------------|
| Connaître l’**id** de l’entreprise de l’utilisateur connecté | Après login (ou au démarrage de l’app si un token est déjà en mémoire), appeler **`GET /api/companies/my/`** avec `Authorization: Token …`. En **200**, l’objet entreprise a un champ **`id`** (entier) : c’est cette valeur qu’il faut **stocker** (contexte React, store, etc.) et réutiliser comme **`company_id`** dans les corps qui l’exigent (ex. **`POST /api/auth/invite-user/`**). |
| Utilisateur **sans** entreprise en base | Si **`GET /api/companies/my/`** répond **404** avec `error: "Profil non trouvé"` / `detail` sur l’absence d’entreprise, le compte n’a **pas** de **`UserProfile`** lié à une **`Company`**. Aucun `company_id` n’existe pour lui tant que ce lien n’est pas créé (inscription **`POST /api/auth/register/`** qui crée company + profil, **invitation** `invite-user`, ou action admin Django sur `UserProfile`). |
| Création de clients, produits, commandes, etc. | Beaucoup de vues utilisent **`request.user.userprofile.company`** (mixin) : **tu n’envoies en général pas** `company_id` dans le body. En revanche il faut un **profil valide** ; sinon le backend peut renvoyer une erreur du type *profil / entreprise manquant* (selon l’endpoint). |

**Check-list intégration Next.js (recommandée)**

1. Login → sauver `token`.
2. **`GET /api/companies/my/`** → sauver `id` comme **`currentCompanyId`** (nom au choix).
3. Pour **`POST /api/auth/invite-user/`**, inclure dans le body : `"company_id": <currentCompanyId>` (plus les autres champs requis : `email`, `first_name`, `last_name`, `role`, etc.).
4. Si l’étape 2 échoue en **404**, ne pas afficher « company manque » comme bug réseau : guider vers **association à une entreprise** — voir **§1.6.1** ci-dessous (message type front : *« Votre compte n’est associé à aucune entreprise »*).

#### 1.6.1 Dépannage : 404 sur `GET /api/companies/my/` — que faire concrètement ?

**Pourquoi** : l’endpoint s’appuie sur un enregistrement **`UserProfile`** (liaison **OneToOne** utilisateur ↔ **une** `Company`). Sans ce lien, la réponse est **404** (`Profil non trouvé` / non associé à une entreprise). Être **connecté** (token valide) **ne suffit pas**.

**Cas fréquent** : compte créé via **`POST /api/permissions/users/`**, **`createsuperuser`**, ou import : tu as un **`User`** (et parfois des **`UserRole`**), mais **pas** de **`UserProfile`**.

| Objectif | Action |
|----------|--------|
| **Réutiliser ton compte actuel** (ex. `admin@nodus.local`) | Créer le **`UserProfile`** à la main : **admin Django** → *Profils utilisateurs* → **Ajouter** → choisir **Utilisateur** + **Entreprise** (existante). Cocher **Admin de l’entreprise** si ce compte doit tout gérer côté tenant. Puis te **reconnecter** ou rafraîchir : **`GET /api/companies/my/`** doit passer en **200**. |
| **Aucune entreprise en base** | Créer d’abord une **`Company`** (admin Django *Entreprises*, ou script / `populate`), **puis** lier ton user avec un **`UserProfile`** comme ci-dessus. |
| **Nouveau workspace from scratch** (nouvel email acceptable) | **`POST /api/auth/register/`** : crée **User + Company + UserProfile + rôle Admin** en un flux. Ne convient pas si tu veux garder le même user Django sans doublon. |
| **Invitation (`invite-user`)** | Crée un **nouvel** utilisateur (email invité) **avec** `UserProfile`. Ça ne « répare » **pas** un compte **déjà existant** sans profil : pour **toi**, privilégier **admin** ou **shell**. |

**Exemple shell Django** (à adapter : email, id entreprise) :

```bash
cd /chemin/vers/erp_backend && source venv/bin/activate
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from apps.common.models import Company, UserProfile

User = get_user_model()
u = User.objects.get(email="admin@nodus.local")  # ton compte
c = Company.objects.order_by("id").first()       # ou .get(id=1)
UserProfile.objects.update_or_create(
    user=u,
    defaults={"company": c, "is_company_admin": True},
)
```

Ensuite **`GET /api/companies/my/`** doit renvoyer l’entreprise : le front pourra proposer **créer / inviter un membre** avec un vrai **`company_id`**.

**Note** : ce backend **ne** documente **pas** ici de header du type `X-Company-Id` pour le multi-tenant : le périmètre entreprise repose sur le **`UserProfile`** de l’utilisateur authentifié (sauf endpoints « voir toutes les companies » avec permission dédiée).

### 1.7 « Configurations » Nodus : pourquoi ça ne semble pas branché malgré la connexion

**Symptôme** : tu es **authentifié** (token OK), mais l’écran **Paramètres / Configurations** (thème, langue, couleurs, etc.) **ne reflète pas** ce qui vient du serveur, ou les changements **ne sont jamais sauvegardés** côté API.

**Explication** : dans ce dépôt, **la connexion** (`login`) et **les préférences d’affichage ou métier** sont **deux flux distincts** :

| Couche | Rôle |
|--------|------|
| **Auth** | `POST /api/auth/login/` → `token` + `user` (champs utilisateur Django de base). **Aucune** préférence UI ni objet `settings` complet dans cette réponse. |
| **Entreprise (lecture)** | **`GET /api/companies/my/`** (token requis) → objet **Company** : notamment **`primary_color`**, **`settings`** (JSON libre, dictionnaire), **`name`**, **`logo` / `logo_url`**, coordonnées, etc. C’est **la** source serveur documentée pour **personnaliser l’UI par tenant** (couleur marque, clés métier dans `settings`). |
| **Front Nodus (souvent)** | Beaucoup de réglages vivent encore en **`localStorage`** (ex. thème clair/sombre, langue). Ils **ne passent pas** par l’API → tu peux être « connecté » tout en ayant l’impression que les configs ne sont **pas branchées** : c’est **cohérent** tant que le code front **n’appelle pas** `GET /api/companies/my/` pour **hydrater** l’UI **et** qu’il n’appelle pas **`PATCH` / `PUT /api/companies/my/`** pour **persister** `settings` / `primary_color` (voir ci-dessous). |

**Écriture / sauvegarde serveur (réalité du backend)** :

- **`PATCH` / `PUT /api/companies/my/`** (token + **`UserProfile`**) : mise à jour de **l’entreprise courante** (champs modifiables : voir **§1.8**). Pas de champ **`is_active`** sur cette route (pas de désactivation du tenant via l’API self-service).
- Les autres URLs entreprise restent en **lecture** : **`GET /api/companies/{id}/`**, **`GET /api/companies/`** (liste, permission `companies_view_all`).
- Il **n’existe pas** d’endpoint dédié **`/preferences`** : les préférences UI vivent typiquement dans **`Company.settings`** (JSON) + **`PATCH /api/companies/my/`**.

**Comment « brancher » correctement côté front (lecture — faisable tout de suite)** :

1. Après login (ou au refresh de session avec token valide), appeler **`GET /api/companies/my/`** (même flux que **§1.6**).
2. En **200**, utiliser au minimum :
   - **`primary_color`** → variable CSS (`--primary`) ou thème du design system ;
   - **`settings`** → objet JSON : conventionner des clés (ex. `theme`, `locale`) **au sein de l’équipe** et les lire pour initialiser le store UI **en plus** ou **à la place** du `localStorage` pour ces clés ;
   - **`name`**, **`logo_url`** pour l’en-tête / marque blanche.
3. Si tu gardes `localStorage` pour le confort offline : documenter que c’est **priorité locale** vs serveur, ou **fusion** explicite (ex. serveur à l’ouverture de session, puis **`PATCH /api/companies/my/`** pour renvoyer `settings` / `primary_color` au serveur quand l’utilisateur enregistre).

**Exemple (extrait de réponse `GET /api/companies/my/`)** :

```json
{
  "id": 1,
  "name": "Ma société",
  "primary_color": "#2E8B57",
  "settings": {
    "theme": "dark",
    "locale": "fr"
  },
  "logo_url": null
}
```

> Les clés à l’intérieur de **`settings`** ne sont pas imposées par ce contrat : c’est un **JSON libre** côté modèle `Company` ; l’équipe produit doit **se mettre d’accord** sur le schéma pour que le front et **`PATCH /api/companies/my/`** restent alignés.

### 1.8 Profil utilisateur connecté & infos boutique — lecture et écriture

Cette section répond explicitement : *« Comment connecter le front pour afficher / modifier le profil connecté et les infos de la boutique ? »*

#### Lecture

| Besoin UI | Appel API | Headers | Réponse utile |
|-----------|-----------|---------|----------------|
| **Afficher l’utilisateur connecté** (nom, email, etc.) | **`GET /api/auth/profile/`** | `Authorization: Token <token>` | Objet **user** : `id`, `username`, `email`, `first_name`, `last_name`, `is_active`, `date_joined`. |
| **Afficher la boutique / tenant courant** | **`GET /api/companies/my/`** | idem | Objet **Company** complet (lecture) — voir **§1.7**. |

**Séquence front recommandée (affichage)** : après login → **`GET /api/auth/profile/`** + **`GET /api/companies/my/`** (si **404** sur la company → **§1.6**).

#### Écriture (implémenté)

| Besoin UI | Appel API | Corps (exemples) | Réponse / erreurs |
|-----------|-----------|------------------|-------------------|
| **Enregistrer** le profil connecté | **`PATCH`** ou **`PUT`** **`/api/auth/profile/`** | JSON partiel ou complet : **`first_name`**, **`last_name`**, **`email`**. | **200** : même forme que **`GET`** (objet user à jour). **`email`** : unicité vérifiée ; en cas de changement, **`username`** est aligné sur **`email`** (convention identique à l’invitation). **400** : erreurs de validation (ex. email déjà pris). |
| **Enregistrer** la boutique | **`PATCH`** ou **`PUT`** **`/api/companies/my/`** | Champs acceptés (tous optionnels en **PATCH**) : **`name`**, **`logo`** (fichier en **multipart/form-data** si upload), **`primary_color`**, **`description`**, **`email`**, **`phone`**, **`address`**, **`city`**, **`postal_code`**, **`country`**, **`website`**, **`tax_number`**, **`registration_number`**, **`settings`** (objet JSON). | **200** : objet **Company** complet (même serializer qu’en **GET**). **404** : pas de **`UserProfile`** (**§1.6**). **400** : validation serializer. |

**Non exposé** via ces routes self-service : **`is_active`** du user, **`is_active`** de la **Company** (désactivation tenant), rôles / permissions — utiliser **admin Django** ou **`/api/permissions/users/`** pour l’administration.

**Alternative admin** : un compte avec **`users_manage`** peut toujours utiliser **`PATCH /api/permissions/users/{id}/`** pour modifier un autre utilisateur (ou le sien si l’**`id`** est connu) ; ce n’est pas le flux « page profil » grand public.

---

## 2) Conventions de réponses

### 2.1 Pagination (DRF standard)
Sur les endpoints “list” (ex: products, customers, orders, movements) :

```json
{
  "count": 123,
  "next": "http://127.0.0.1:8000/api/.../?page=2",
  "previous": null,
  "results": []
}
```

### 2.2 Formats d’erreurs observés (front doit supporter)

#### A) Permission (RBAC)
```json
{
  "error": "Permission refusée",
  "detail": "Vous n'avez pas la permission de …",
  "required_permission": "stock_view"
}
```

#### B) Erreur simple (ex: login)
```json
{ "error": "Email ou mot de passe incorrect" }
```

#### C) Enveloppe `success/error` (dashboard/analytics)
```json
{
  "success": false,
  "error": { "code": "…", "message": "…", "details": "…" }
}
```

#### D) Pas d’entreprise liée au compte (`GET /companies/my/`)
```json
{
  "error": "Profil non trouvé",
  "detail": "Vous n'êtes associé à aucune entreprise"
}
```
→ **404** : le front ne doit pas inventer de `company_id` ; traiter comme compte non rattaché (voir **§1.6**).

#### E) Champ `company_id` manquant ou invalide (ex. `invite-user`)
Réponse typique **400** (erreurs de validation DRF), par ex. :
```json
{
  "company_id": ["Ce champ est obligatoire."]
}
```
ou message sur entreprise inexistante / inactive selon `InviteUserSerializer`.

---

## 3) RBAC / Permissions

La majorité des endpoints nécessitent :
- utilisateur authentifié (**IsAuthenticated**)
- et une permission via `user_has_permission(...)`.

### 3.1 Superuser Django et rôle ERP « Admin »
Les vérifications RBAC métier accordent **toutes** les permissions (y compris `users_manage`, `stock_view`, etc.) si :
- l’utilisateur est **superuser Django** (`is_superuser`), **ou**
- il a un **`UserRole` actif** (non expiré) avec le rôle nommé exactement **`Admin`**.

Le nom du rôle en base doit être **`Admin`** (casse sensible) : ce n’est **pas** le même concept que le flag `is_staff` / accès `/admin/` Django.

### 3.2 Seed des rôles / permissions via migrations (recommandé)

Le projet contient des migrations de données qui préparent automatiquement :

- les rôles système de base (`Admin`, `User`) ;
- les permissions (`Permission`) utilisées par les vues ;
- la matrice `RolePermission` par rôle métier.

Commande à lancer sur chaque environnement :

```bash
python manage.py migrate
```

Ensuite, en cas d’ajout futur de nouvelles permissions côté code, tu peux réaligner rapidement le rôle `Admin` :

```bash
python manage.py sync_admin_permissions
```

### 3.3 Politique de restrictions par type d’utilisateur (RBAC)

La politique appliquée est :

| Rôle | Périmètre |
|---|---|
| `Admin` | Toutes les permissions (métier + utilisateurs + rôles + permissions + entreprises globales) |
| `Manager` | Dashboard, clients, inventaire, stock, ventes, alertes, notifications (toutes actions) |
| `Inventory Manager` | Inventaire uniquement (`inventory*`) |
| `Stock Manager` | Stock uniquement (`stock*`) |
| `Sales Manager` | Ventes uniquement (`sales*`) |
| `User` | Lecture seule (`action=view`) sur le périmètre métier (dashboard, clients, inventaire, stock, ventes, alertes, notifications) |

Points importants :

- **seul `Admin`** peut gérer les utilisateurs et le RBAC (`users_manage`, `permissions_*`, `roles_*`) ;
- un `superuser` Django garde aussi un accès total (bypass) ;
- le `Manager` n’a pas les permissions d’administration des comptes.

### 3.4 Multi-tenant : une base partagée, isolation par `Company` (comportement actuel)

**Question fréquente** : « Pourquoi je vois des clients d’autres entreprises ? Je veux une base vide pour Nodus et un seul compte admin boutique. »

| Point | Détail |
|-------|--------|
| Base **par** entreprise ? | **Non** : une **seule** base, tables communes, FK **`company`** sur les modèles métier (clients, commandes, produits, …). |
| Qui voit **toutes** les entreprises ? | Uniquement les **`is_superuser=True`** Django (accès plateforme / admin Django). Le **rôle ERP `Admin`** et les autres utilisateurs sont **limités** à **`UserProfile.company`** dans **`CompanyFilterMixin`**, le **dashboard**, **analytics** et les KPI clients alignés. |
| Compte boutique « tout pouvoir » sans voir les autres tenants | Utiliser un utilisateur **`is_superuser=False`** avec rôle **`Admin`** + **`UserProfile`** sur **ta** `Company` → toutes les permissions API (**§3.1**), mais **données filtrées** sur cette société uniquement. |
| Liste **tous** les utilisateurs Django | **`GET /api/permissions/users/`** reste un **catalogue global** (pas filtré par company dans ce dépôt) — normal si tu gères l’auth côté serveur ; le front peut filtrer ou une évolution API peut restreindre. |

**Repartir sur une base vide + une entreprise Nodus + un admin boutique** (à lancer sur ta machine, **backup** avant `--fresh`) :

```bash
source venv/bin/activate
python manage.py bootstrap_nodus_tenant --fresh --email boutique@nodus.local --password "TonMotDePasse" --company "Nodus"
```

- **`--fresh`** : vide les données métier dans un **ordre compatible avec les FK `PROTECT`** (factures → commandes → stock → catalogue → clients → profils → rôles → entreprises), puis supprime **tous les `User` non superuser** et recrée l’entreprise et le compte demandés. (Un simple `Company.objects.all().delete()` **échoue** à cause de ces protections.)
- Le compte créé n’est **pas** superuser : il **ne voit que** sa boutique.
- Les **superusers** éventuels sont **conservés** ; ils voient encore **tout** (utile pour l’admin Django).

Ensuite : connecter le front avec cet **email** / mot de passe → **`GET /api/companies/my/`** doit renvoyer **ta** société vide.

---

## 4) Endpoints — Table de référence (routes réelles)

> Base : toutes les URLs ci-dessous sont préfixées par `/api`.

### 4.1 Auth / Company / Alerts / Notifications (`apps/common/urls.py`)

| Domaine | Méthode | Chemin | Auth | Permission | Notes |
|---|---:|---|---|---|---|
| Auth | POST | `/auth/register/` | non | — | Inscription + crée company + assigne rôle `Admin` |
| Auth | POST | `/auth/login/` | non | — | Retourne `{token, user, message}` |
| Auth | POST | `/auth/logout/` | oui | — | Invalide le token |
| Auth | GET | `/auth/profile/` | oui | — | User courant — **§1.8** |
| Auth | PATCH, PUT | `/auth/profile/` | oui | — | Mise à jour self-service (`first_name`, `last_name`, `email`) — **§1.8** |
| Auth | POST | `/auth/refresh-token/` | oui | — | À confirmer comportement |
| Auth | POST | `/auth/invite-user/` | oui | `users_manage` | Invite un user dans la company |
| Company | GET | `/companies/my/` | oui | — | Company de l’utilisateur ; **`primary_color`**, **`settings`** — **§1.7** |
| Company | PATCH, PUT | `/companies/my/` | oui | — | Mise à jour boutique (sans `is_active` company) — **§1.8** |
| Company | GET | `/companies/{company_id}/` | oui | `companies_view_all` si hors company | Accès restreint |
| Alerts | GET | `/alerts/` | oui | — | Pagination custom (pas DRF) selon impl |
| Notifications | GET | `/notifications/` | oui | — | Idem |

> **Mise à jour de l’entreprise** : **`PATCH` / `PUT /api/companies/my/`** — **§1.8** (champs modifiables listés là ; pas de désactivation du tenant via cette route).

### 4.2 Customers (`/customers/` — `apps/customers/views.py`)

| Ressource | Méthode | Chemin | Permission | Pagination | Notes |
|---|---:|---|---|---|---|
| Customers | GET | `/customers/` | `customers_view` | DRF (`count/next/previous/results`) | filtres + search + ordering |
| Customers | POST | `/customers/` | `customers_create` | — | utilise `CustomerCreateSerializer` |
| Customer | GET | `/customers/{id}/` | `customers_view` | — | |
| Customer | PATCH | `/customers/{id}/` | `customers_update` | — | |
| Customer | DELETE | `/customers/{id}/` | `customers_delete` | — | soft delete (voir code) |
| Customers KPI | GET | `/customers/analytics/kpis/` | (selon impl) | — | |

### 4.3 Inventory — Categories / Products / Variants (`/inventory/` — `apps/inventory/urls.py`)

#### Catégories
| Ressource | Méthode | Chemin | Permission | Notes |
|---|---:|---|---|---|
| Categories | GET | `/inventory/categories/` | `inventory_category.view` | |
| Categories | POST | `/inventory/categories/` | `inventory_category.create` | |
| Category | GET | `/inventory/categories/{id}/` | `inventory_category.view` | |
| Category | PATCH | `/inventory/categories/{id}/` | `inventory_category.update` | |
| Category | DELETE | `/inventory/categories/{id}/` | `inventory_category.delete` | |
| Categories | GET | `/inventory/categories/active/` | `inventory_category.view` | action |
| Category | GET | `/inventory/categories/{id}/products/` | `inventory_category.view` | action |

#### Produits
| Ressource | Méthode | Chemin | Permission | Pagination | Notes |
|---|---:|---|---|---|---|
| Products | GET | `/inventory/products/` | `inventory_view` | DRF | `search`, `ordering`, `filterset_fields` |
| Products | POST | `/inventory/products/` | `inventory_create` | — | `ProductCreateSerializer` |
| Product | GET | `/inventory/products/{id}/` | `inventory_view` | — | |
| Product | PATCH | `/inventory/products/{id}/` | `inventory_update` | — | `ProductUpdateSerializer` |
| Product | DELETE | `/inventory/products/{id}/` | `inventory_delete` | — | |
| Products | POST | `/inventory/products/with-variants/` | `inventory_create` | — | création produit + variants |

#### Variants
| Ressource | Méthode | Chemin | Permission | Notes |
|---|---:|---|---|---|
| Variants | GET | `/inventory/variants/` | (voir views) | Router DRF |
| Variants | POST | `/inventory/variants/` | (voir views) | Router DRF |

### 4.4 Stock (`/stock/` — `apps/stock/views.py`)

#### Mouvements
| Ressource | Méthode | Chemin | Permission | Pagination | Notes |
|---|---:|---|---|---|---|
| Movements | GET | `/stock/movements/` | `stock_view` | DRF | `filterset_fields` inclut `product`, `movement_type`, etc. |
| Movements | POST | `/stock/movements/` | `stock_manage` | — | `StockMovementCreateSerializer` |
| Movement | GET | `/stock/movements/{id}/` | `stock_view` | — | |
| Movement | PATCH | `/stock/movements/{id}/` | `stock_manage` | — | |
| Movement | DELETE | `/stock/movements/{id}/` | `stock_manage` | — | |
| Movements | GET | `/stock/movements/summary/` | `stock_view` | — | action |
| Movements | POST | `/stock/movements/{id}/approve/` | `stock_manage` | — | action |
| Movements | POST | `/stock/movements/{id}/reject/` | `stock_manage` | — | action |

### 4.5 Sales (`/sales/` — `apps/sales/views.py`)

#### Orders
| Ressource | Méthode | Chemin | Permission | Pagination | Notes |
|---|---:|---|---|---|---|
| Orders | GET | `/sales/orders/` | `sales_order.view` | DRF | filtres: `customer`, `status`, `user` |
| Orders | POST | `/sales/orders/` | `sales_order.create` | — | `OrderCreateSerializer` (items requis) |
| Order | GET | `/sales/orders/{id}/` | `sales_order.view` | — | |
| Order | PATCH | `/sales/orders/{id}/` | ⚠️ `sales_orders_create` | — | Incohérence dans le code : permission “create” utilisée pour update/delete |
| Order | DELETE | `/sales/orders/{id}/` | ⚠️ `sales_orders_create` | — | idem |
| Order | POST | `/sales/orders/{id}/confirm/` | ⚠️ `sales_orders_create` | — | action statut |
| Order | POST | `/sales/orders/{id}/ship/` | ⚠️ `sales_orders_create` | — | action statut |
| Order | POST | `/sales/orders/{id}/deliver/` | ⚠️ `sales_orders_create` | — | action statut |
| Order | POST | `/sales/orders/{id}/cancel/` | ⚠️ `sales_orders_create` | — | action statut |
| Orders | GET | `/sales/orders/summary/` | `sales_order.view` | — | action résumé |

> Note : le contrat “status-history” n’existe pas sous la forme du MD UX. Ici, le statut est géré via des actions dédiées.

### 4.6 Dashboard (`/dashboard/` — `apps/dashboard/urls.py`)
| Endpoint | Méthode | Chemin | Notes |
|---|---:|---|---|
| KPIs | GET | `/dashboard/kpis/` | Réponse `{success: true, data: {...}}` |
| Overview | GET | `/dashboard/overview/` | ⚠️ a déjà renvoyé 500 en local (bug à corriger avant staging) |
| Sales chart | GET | `/dashboard/sales-chart/` | |
| Top products | GET | `/dashboard/top-products/` | |
| Clients distribution | GET | `/dashboard/clients-distribution/` | |
| Alerts | GET | `/dashboard/alerts/` | |
| Recent orders | GET | `/dashboard/recent-orders/` | |
| Recent invoices | GET | `/dashboard/recent-invoices/` | |

### 4.7 Membres / équipe / utilisateurs (`/permissions/` — `apps/permissions/` + invitation `apps/common/`)

Dans ce backend, il **n’existe pas** de ressource nommée `/members` comme dans certains contrats UX. L’équivalent métier est :

- **Utilisateurs Django** : table `auth_user`, exposés sous **`/api/permissions/users/`**
- **Rôles ERP** : modèle `Role` + liaison `UserRole`, exposés sous **`/api/permissions/user-roles/`** et actions sur un user
- **Membre rattaché à une entreprise** : modèle **`UserProfile`** (`user` → `company`), créé notamment par **`POST /api/auth/invite-user/`** (pas automatiquement par toutes les routes de création d’utilisateur)

#### Auth commune à toutes ces routes
```
Authorization: Token <token>
Content-Type: application/json
```

#### Permission critique : `users_manage`
Pour **lister**, **créer**, **modifier**, **supprimer** des utilisateurs via le `UserViewSet` et les endpoints `admin/create-user/`, le backend vérifie la permission codename **`users_manage`**.

Si ton utilisateur connecté **ne l’a pas** (non liée au rôle dans `RolePermission`), tu obtiens typiquement :

```json
{
  "error": "Permission refusée",
  "detail": "Vous n'avez pas la permission de voir les utilisateurs",
  "required_permission": "users_manage"
}
```

**Conséquence front** : page “membres” vide ou impossible d’ajouter un user → regarder le **status HTTP 403** et le champ **`required_permission`** ; puis **assigner `users_manage`** au rôle de l’utilisateur (via admin Django, script, ou données `RolePermission`), ou te connecter avec un compte qui l’a déjà.

> **Rappel** : le rôle ERP **`Admin`** actif (ou **superuser**) donne **toutes** les permissions via **`user_has_permission`** (voir **§3.1**). La commande **`sync_admin_permissions`** sert surtout à aligner les lignes **`RolePermission`** en base.

#### Lister les utilisateurs (“membres” côté auth)
| Action | Méthode | Chemin | Permission | Pagination | Notes |
|---|---:|---|---|---|---|
| Liste paginée | GET | `/permissions/users/` | `users_manage` | DRF | `?search=`, filtres `is_active`, `is_staff`, `is_superuser`, `ordering` |
| Utilisateurs actifs | GET | `/permissions/users/active/` | `users_manage` | — | réponse **liste** (pas paginée DRF sur cette action) |
| Staff | GET | `/permissions/users/staff/` | `users_manage` | — | idem |
| Détail | GET | `/permissions/users/{id}/` | `users_manage` | — | |
| Résumé | GET | `/permissions/users/summary/` | `users_manage` | — | compteurs |
| Rôles d’un user | GET | `/permissions/users/{id}/roles/` | `users_manage` | — | |

**Note** : le `UserViewSet` utilise `queryset = User.objects.all()` : la liste peut contenir **tous** les utilisateurs Django, pas seulement ceux de ta société. Le front peut filtrer (ex. par email, recherche) ou s’appuyer sur **`UserProfile`** / métier pour restreindre l’affichage.

#### Créer un utilisateur (deux chemins principaux)

**A) Création “admin” (mot de passe choisi par toi)** — même permission `users_manage`

| Méthode | Chemin | Body |
|---|---|---|
| POST | `/permissions/users/` | `UserCreateSerializer` (voir §5.4) |
| POST | `/permissions/admin/create-user/` | idem (wrapper qui renvoie `{ user, message }`) |

⚠️ Ce flux crée le **`User`** (+ **`UserRole`** si `role_ids` fourni). Il **ne crée pas** automatiquement un **`UserProfile`** lié à une **`Company`**. Si ton front considère un “membre” comme quelqu’un de **l’entreprise**, il peut manquer le profil : préférer **l’invitation (B)** ou compléter côté backend plus tard.

**B) Invitation (mot de passe temporaire + entreprise + rôle ERP)** — permission `users_manage`

| Méthode | Chemin | Notes |
|---|---|---|
| POST | `/auth/invite-user/` | Crée `User` (**username = email**), `UserRole`, **`UserProfile`** avec `company_id` ; mot de passe **aléatoire 12 caractères** (réponse ou email) |

#### Gérer les rôles d’un utilisateur existant
| Action | Méthode | Chemin | Permission | Body (exemple) |
|---|---:|---|---|---|
| Assigner un rôle | POST | `/permissions/users/{id}/assign_role/` | `users_manage` | `{ "role_id": 1, "expires_at": null, "notes": "" }` |
| Retirer un rôle | POST | `/permissions/users/{id}/remove_role/` | `users_manage` | `{ "role_id": 1 }` |
| Reset mot de passe | POST | `/permissions/users/{id}/reset_password/` | `users_manage` | `{ "new_password": "…" }` |
| Activer / désactiver | POST | `/permissions/users/{id}/activate/` ou `.../deactivate/` | `users_manage` | — |

#### Rôles disponibles (pour remplir `role` ou `role_ids`)
| Action | Méthode | Chemin | Permission |
|---|---:|---|---|
| Liste | GET | `/permissions/roles/` | `permissions_roles_view` |
| Actifs | GET | `/permissions/roles/active/` | `permissions_roles_view` |

Le champ `role` de **`invite-user`** attend le **nom** du rôle tel qu’en base (ex. `"Admin"`, `"User"`, `"Manager"`, `"Inventory Manager"`, `"Stock Manager"`, `"Sales Manager"`), pas l’id.

#### Récupérer `company_id` pour une invitation
| Méthode | Chemin |
|---|---|
| GET | `/companies/my/` |

Le champ à utiliser dans le body d’**`invite-user`** est l’entier **`id`** de l’objet JSON retourné par **`GET /companies/my/`** (pas un champ nommé `company_id` dans cette réponse). Voir **§1.6**.

#### Autres endpoints utiles
| Méthode | Chemin | Permission |
|---|---|---|
| GET | `/permissions/user-permissions/{user_id}/` | `permissions_user_roles_view` |
| GET | `/permissions/admin/user-permissions/{user_id}/` | `users_manage` |
| POST | `/permissions/admin/bulk-assign-roles/` | `users_manage` |

#### Dépannage : « liste vide » ou « impossible d’ajouter un user »

| Symptôme | Cause probable | Action |
|---|---|---|
| **403** sur `GET /permissions/users/` | Pas de permission **`users_manage`** | Lier la permission au rôle de l’utilisateur connecté (`RolePermission`), ou utiliser un superuser / compte déjà autorisé |
| **403** sur `GET /permissions/roles/` | Pas de **`permissions_roles_view`** | Idem côté `RolePermission` |
| **201** invitation / création mais l’user « n’existe pas » dans le shell avec un mauvais email | **Username** = email pour les invités ; email mal saisi | `User.objects.filter(username__icontains="…")` ou liste dans l’admin `/admin/` |
| User créé via `/permissions/users/` invisible côté “entreprise” | Pas de **`UserProfile`** + **`company`** | Utiliser **`invite-user`** ou créer le profil (évolution backend) |
| **200** mais liste vide côté UI | Front filtre trop (société) alors que l’API renvoie tout `User` | Vérifier la réponse brute `results` / `count` ; aligner filtre front ou ajouter filtre API |
| **Utilisateurs désactivés toujours visibles** | **`GET /api/permissions/users/`** renvoie **tous** les `User` par défaut (`is_active` true **et** false) | Côté API : **`?is_active=true`** pour n’afficher que les actifs, ou **`GET /api/permissions/users/active/`** (liste non paginée). Côté front : appliquer le même filtre après `GET` ou rafraîchir la liste après **`deactivate`**. |
| **Nouvel utilisateur créé mais rien à l’écran** | Pas de **re-fetch** après **201**, liste en **localStorage**, ou mauvaise **page** pagination | Après **POST** réussi : **`GET /api/permissions/users/?page=1&ordering=-date_joined`** (ou équivalent) ; ne pas se fier à un état local non synchronisé. |
| **Création membre OK mais pas « dans l’entreprise »** | **POST `/permissions/users/`** sans **`UserProfile`** | Préférer **`invite-user`** ou créer le **`UserProfile`** (admin Django). |

---

## 5) Payloads (exemples “create/update”) — alignés sur les serializers

### 5.1 Customers — créer
Endpoint : **POST** `/api/customers/` (permission `customers_create`)

```json
{
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean.dupont@example.com",
  "phone": "+33...",
  "client_company": "ACME",
  "address": "1 rue ...",
  "city": "Paris",
  "postal_code": "75001",
  "country": "FR",
  "notes": "…"
}
```

### 5.2 Orders — créer (avec items requis)
Endpoint : **POST** `/api/sales/orders/` (permission `sales_order.create`)

```json
{
  "customer": 123,
  "status": "pending",
  "order_date": "2026-04-09T10:00:00Z",
  "delivery_date": null,
  "tax_rate": 20,
  "discount_rate": 0,
  "notes": "…",
  "internal_notes": "…",
  "items": [
    {
      "product": 10,
      "variant": 55,
      "quantity": 2,
      "unit_price": 15000,
      "discount_rate": 0
    }
  ]
}
```

### 5.3 Products — créer (`ProductCreateSerializer`)
Endpoint : **POST** `/api/inventory/products/` (permission **`inventory_create`**)

**Champs acceptés dans le JSON** (corps typique `Content-Type: application/json`) :  
`name`, `description`, `short_description`, `sku`, `barcode`, `category` (**id** de catégorie existante **de ton entreprise**), `product_type`, `status`, `price`, `cost_price`, `weight`, `dimensions`, `is_digital`, `is_featured`, `tags`, `meta_title`, `meta_description`, et optionnellement `images` (liste d’objets — voir ci‑dessous).

```json
{
  "name": "Produit A",
  "description": "…",
  "short_description": "…",
  "sku": "SKU-001",
  "barcode": "123456789",
  "category": 1,
  "product_type": "simple",
  "status": "active",
  "price": "100.00",
  "cost_price": "60.00",
  "weight": "1.2",
  "dimensions": "10x20x30",
  "is_digital": false,
  "is_featured": false,
  "tags": "tag1,tag2",
  "meta_title": "…",
  "meta_description": "…"
}
```

**Pourquoi le front a l’impression que « tout n’est pas pris »**

| Sujet | Réalité backend |
|--------|------------------|
| **Champs non listés** | Seuls les champs du **serializer de création** sont enregistrés. Pas de variantes dans le POST simple : **`POST /api/inventory/products/with-variants/`** ou ensuite **`POST /api/inventory/product-variants/`**. |
| **Images fichiers** | `ProductImage` en base utilise un **`ImageField`** (fichier). Le champ JSON `images` attend des structures compatibles avec **`ProductImage.objects.create`** : en pratique, envoyer de **vrais fichiers** via **multipart/form-data** ou un **endpoint d’upload** dédié est nécessaire ; un JSON pur **sans** fichier **ne peut pas** remplir l’image comme en UI classique. Si le front n’envoie que du texte, les images seront absentes ou la requête échouera. |
| **Catégorie** | `category` doit être l’**id** d’une **`Category`** déjà créée pour **ta** `Company` ; sinon erreur de validation. |
| **Profil sans entreprise** | Sans **`UserProfile`** + **`Company`**, la création peut renvoyer une erreur *profil / entreprise* (voir **§1.6**). |

### 5.3b Products — mise à jour (PATCH / PUT)
Endpoint : **PATCH** ou **PUT** `/api/inventory/products/{id}/` (permission **`inventory_update`** — **pas** `inventory_create`)

> Même utilisateur : vérifie que le rôle inclut bien **`inventory_update`** (ou rôle ERP **Admin** / superuser qui bypass). Un 403 avec `required_permission: inventory_update` explique un « modifier qui ne marche pas ».

Le serializer **`ProductUpdateSerializer`** accepte les mêmes champs métier que la création **plus** : `images` (mise à jour d’images existantes / création) et `images_to_delete` (liste d’ids). Mêmes limites que pour les **fichiers image** : les uploads réels passent par **fichiers** ou flux prévu côté API.

### 5.4 Membres — invitation (recommandé pour un membre d’entreprise)
Endpoint : **POST** `/api/auth/invite-user/` (permission `users_manage`)

```json
{
  "email": "nouveau@example.com",
  "first_name": "Prénom",
  "last_name": "Nom",
  "role": "Admin",
  "company_id": 1,
  "send_email": false
}
```

- Si **`send_email`: false** : la réponse API contient souvent **`temp_password`** (à afficher une fois côté UI ou à transmettre hors bande).
- Si **`send_email`: true** : le mot de passe part par **email** (config SMTP requise).

### 5.5 Membres — création admin (mot de passe défini par toi)
Endpoint : **POST** `/api/permissions/users/` ou **POST** `/api/permissions/admin/create-user/` (permission `users_manage`)

```json
{
  "username": "nouveau.user",
  "email": "nouveau@example.com",
  "password": "MotDePasseLong8+",
  "password_confirm": "MotDePasseLong8+",
  "first_name": "Prénom",
  "last_name": "Nom",
  "is_active": true,
  "is_staff": false,
  "is_superuser": false,
  "role_ids": [1]
}
```

- **`role_ids`** : liste d’**IDs** de rôles (voir `GET /api/permissions/roles/`).
- Pense à lier l’utilisateur à une **entreprise** si ton métier l’exige : ce serializer **ne crée pas** `UserProfile` tout seul.

---

## 6) Test plan local (reproductible par le front)

1. **Login** : `POST /api/auth/login/` → récupérer `token`
2. **Entreprise** : `GET /api/companies/my/` → récupérer **`id`** (pour **`company_id`**, **§1.6**) **et** **`primary_color` + `settings`** pour hydrater l’UI « configurations » (**§1.7**)
3. **Profile** : `GET /api/auth/profile/` ; test écriture : **`PATCH /api/auth/profile/`** avec `{"first_name":"…"}` → **200** et user mis à jour (**§1.8**)
4. **Boutique (écriture)** : **`PATCH /api/companies/my/`** avec par ex. `{"primary_color":"#2E8B57","settings":{"theme":"dark"}}` → **200** (**§1.8**)
5. **Membres** : `GET /api/permissions/users/?page=1` → si **403** + `required_permission: users_manage`, corriger les **RolePermission** avant de debugger le front
6. **Rôles** : `GET /api/permissions/roles/` (permission `permissions_roles_view`) pour alimenter les selects `role` / `role_ids`
7. **Products** : `GET /api/inventory/products/?page=1`
8. **Customers** : `GET /api/customers/?page=1`
9. **Orders** : `GET /api/sales/orders/?page=1`
10. **Stock movements** : `GET /api/stock/movements/?page=1`
11. **Dashboard** : `GET /api/dashboard/kpis/`

---

## 7) Notes d’écarts vs le MD UX initial

- Les routes sont **segmentées par module** (`/inventory`, `/sales`, `/stock`) et pas en ressources racine (`/products`, `/orders`).
- Pagination = **DRF** (`results/count`), pas `{items,total}`.
- Auth = **Token DRF** (`Authorization: Token …`), pas `Bearer`.
- “Order status history” n’est pas exposé tel quel : le statut se gère via actions `confirm/ship/deliver/cancel`.
- **Membres / équipe** : pas de route `/members` ; utiliser **`/api/permissions/users/`** + **`users_manage`**. Pour un membre **lié à l’entreprise** (`UserProfile`), privilégier **`POST /api/auth/invite-user/`** plutôt que la seule création via `/permissions/users/`.

---

## 8) Nodus (front seul, état actuel) — ce qui manque pour une doc / intégration « complète »

Cette section décrit la **réalité du front Nodus aujourd’hui** (comportement constaté dans le code front), par rapport à ce que **ce backend** expose déjà ou pas. Elle complète les §4–7 pour éviter toute ambiguïté entre **démo locale** et **contrat API réel**.

### 8.1 Tableau réalité front ↔ backend

| Élément | Réalité dans le front Nodus (aujourd’hui) | Côté backend (ce dépôt) — piste d’alignement |
|--------|---------------------------------------------|-----------------------------------------------|
| Courbe « évolution du stock » (dashboard stock) | `generateStockHistory` dans `stock-charts.tsx` : **données générées dans le navigateur**, pas un historique serveur. | Pas d’endpoint dédié « historique agrégé pour graphique » dans le contrat actuel. Les **mouvements** existent : `GET /api/stock/movements/` (filtrer par `product`, `date_from` / `date_to` selon impl.). Un endpoint **agrégé** (séries temporelles) resterait à **spécifier / ajouter** si le front doit arrêter le mock. |
| Alertes dashboard (rupture / critique) | Calculées à partir des **produits déjà chargés** en mémoire. | Le backend expose **`GET /api/dashboard/alerts/`**, **`GET /api/stock/alerts/`** (app stock), et des champs KPI côté **`GET /api/dashboard/kpis/`**. Le front **n’utilise pas** encore ces routes pour cette carte. |
| « Activité récente » sur le dashboard | Construite à partir des **commandes déjà listées** côté client. | Le backend expose **`GET /api/dashboard/recent-orders/`** (et d’autres blocs dashboard). Pas d’endpoint unique « activity feed » type UX v1 ; soit **brancher** `recent-orders` + autres, soit **nouveau** `GET /activity` si besoin d’un fil unifié. |
| Membres / équipe | **`localStorage`** (`membres:liste` ou équivalent) : **aucun** appel à `GET /api/permissions/users/`, `POST /api/auth/invite-user/`, etc. | Voir **§4.7** : tout est déjà côté API ; il manque **uniquement le branchement front** + gestion du token et de **`users_manage`**. |
| Préférences UI (thème, langue, etc.) | **`localStorage`** (`user:preferences` ou équivalent). | **Lecture** : **`GET /api/companies/my/`** — **§1.7**. **Écriture serveur** : **`PATCH` / `PUT /api/companies/my/`** avec **`settings`** / **`primary_color`** — **§1.8** (le front peut encore choisir local-first + sync explicite). |
| Profil — bouton Enregistrer | **Non branché** : commentaire / TODO côté front. | **`PATCH` / `PUT /api/auth/profile/`** — **§1.8** (`first_name`, `last_name`, `email`) ; reste à **brancher** l’UI sur cette route. |
| Historique de statut commande (détail) | Historique **reconstruit côté UI** après actions locales ; **pas** de ressource serveur `status-history`. | Conforme à **§7** : statuts gérés par **actions** (`confirm`, `ship`, `deliver`, `cancel`). Un vrai **`OrderStatusHistory`** côté API = **fonctionnalité à ajouter** si l’on veut la même sémantique que l’UX initiale. |

### 8.2 Ce que la doc « complète » doit encore couvrir (spécifiquement Nodus)

Pour considérer la documentation d’intégration **fermée** pour Nodus, il manque encore (au choix : **décision produit** + **spec OpenAPI** ou paragraphes dans ce fichier) :

1. **Courbe stock** : soit contrat d’agrégation (période, granularité, champs), soit convention « le front agrège à partir de `movements` » avec exemples de requêtes.
2. **Alertes** : quelle source fait foi (`dashboard/alerts`, `stock/alerts`, ou calcul client) et champs exacts de réponse.
3. **Activité** : liste des endpoints à composer (`recent-orders`, mouvements récents, etc.) ou nouveau endpoint unique.
4. **Préférences / configuration** : **schéma JSON** pour **`Company.settings`** (convention équipe) — **écriture** : **`PATCH /api/companies/my/`** (**§1.8**).
5. **Profil** : **`PATCH` / `PUT /api/auth/profile/`** documenté (**§1.8**) ; affiner au besoin (mot de passe, avatar, etc.).
6. **Historique commande** : soit on **documente définitivement** le modèle « UI only », soit on **spécifie** une table + `GET /orders/{id}/status-history` (ou équivalent).

### 8.3 Lecture pour l’équipe front

Tant que les lignes du tableau §8.1 restent en **mock / localStorage**, le **contrat backend** de ce fichier décrit ce qui est **disponible pour remplacer** ces comportements ; il ne remplace pas automatiquement l’UI tant que le code Nodus n’appelle pas ces URLs.

### 8.4 Symptômes fréquents (produits, membres, profil) — diagnostic front ↔ API

| Ce que tu vois côté Nodus | Cause côté API / contrat | Action |
|---------------------------|---------------------------|--------|
| **Création produit « ne prend pas tout »** | Le **POST** n’enregistre que les champs du **`ProductCreateSerializer`** ; **variantes** et **images fichiers** ne sont pas le même flux qu’un formulaire HTML unique. | Envoyer le **JSON** complet des champs **§5.3** ; **variantes** → `with-variants` ou **`/inventory/product-variants/`** ; **images** → **multipart** / upload fichier, pas seulement du JSON texte. |
| **Modification produit ne marche pas** | **`PATCH`** `/inventory/products/{id}/` exige **`inventory_update`** (distinct de **`inventory_create`**). | Contrôler **403** + `required_permission` ; compte **Admin** ERP ou superuser bypass ; sinon ajouter **`inventory_update`** au rôle. |
| **Utilisateurs désactivés toujours dans la liste** | **`GET /permissions/users/`** liste **actifs et inactifs** par défaut. | Utiliser **`?is_active=true`** ou **`GET /permissions/users/active/`** ; rafraîchir après `deactivate`. |
| **Ajout d’un user : rien n’apparaît** | **201** OK mais UI ne **recharge** pas l’API ; ou données **mock localStorage**. | Après création : **refetch** `GET /permissions/users/?page=…` ; brancher la page membres sur l’API (**§4.7**). |
| **Impossible de modifier l’utilisateur connecté (profil)** | L’UI n’appelle pas encore **`PATCH /api/auth/profile/`**. | **§1.8** : **`PATCH` / `PUT /auth/profile/`** ; vérifier **400** (validation) et **Token** présent. |

