"""
Règles d’attribution des permissions par rôle (hors migration : logique réutilisable).

- Admin : tout (y compris utilisateurs, RBAC, entreprises globales).
- Manager : tableau de bord, clients, inventaire, stock, ventes, alertes, notifications — pas les users / RBAC / liste globale des sociétés.
- Inventory Manager : module inventaire uniquement.
- Stock Manager : module stock uniquement.
- Sales Manager : module ventes uniquement.
- User : lecture (action « view ») sur les mêmes périmètres métier que Manager (pas users / RBAC / companies).
"""

from __future__ import annotations

# Modules métier : tout sauf gestion des comptes / matrice RBAC / vue multi-tenant globale.
MANAGER_APP_LABELS = frozenset(
    {
        'dashboard',
        'customers',
        'inventory',
        'stock',
        'sales',
        'alerts',
        'notifications',
    }
)


def role_grants_permission(role_name: str, perm) -> bool:
    """Indique si la permission `perm` (modèle historique ou réel) est accordée au rôle `role_name`."""
    app = perm.app_label
    action = (perm.action or '').lower()

    if role_name == 'Admin':
        return True

    if role_name == 'User':
        return action == 'view' and app in MANAGER_APP_LABELS

    if role_name == 'Manager':
        return app in MANAGER_APP_LABELS

    if role_name == 'Inventory Manager':
        return app == 'inventory'

    if role_name == 'Stock Manager':
        return app == 'stock'

    if role_name == 'Sales Manager':
        return app == 'sales'

    return False


def managed_role_names() -> tuple[str, ...]:
    return (
        'Admin',
        'User',
        'Manager',
        'Inventory Manager',
        'Stock Manager',
        'Sales Manager',
    )
