"""
Périmètre multi-tenant : une base partagée, filtrage par Company.

- Superuser Django : accès à toutes les entreprises (exploitation / admin plateforme).
- Autres utilisateurs (y compris rôle ERP Admin) : uniquement les données de
  ``UserProfile.company``. Sans profil : aucune ligne (pas de fuite cross-tenant).
"""

from __future__ import annotations

_MISSING_PROFILE = object()


def get_user_company_or_all(user):
    """
    Retourne :
    - ``None`` : superuser Django → pas de filtre tenant (toutes les companies).
    - ``Company`` : périmètre de l'utilisateur.
    - ``_MISSING_PROFILE`` : pas de UserProfile → filtres impossibles (résultats vides).
    """
    if getattr(user, 'is_superuser', False):
        return None
    try:
        return user.userprofile.company
    except Exception:
        return _MISSING_PROFILE


def is_missing_tenant_profile(scope) -> bool:
    return scope is _MISSING_PROFILE


def company_scope_cache_key_fragment(user_company):
    """Valeur stable pour clés de cache (analytics, etc.)."""
    if user_company is None:
        return 'all'
    if is_missing_tenant_profile(user_company):
        return 'none'
    return user_company.pk


def add_company_filter(target: dict, user_company, path: str = 'company') -> None:
    """
    Ajoute dans ``target`` le filtre FK approprié.

    - ``user_company is None`` (superuser) : ne rien ajouter.
    - profil manquant : ``<path>_id = -1`` (aucune ligne en pratique).
    - sinon : ``path`` = instance Company.
    """
    if user_company is None:
        return
    if user_company is _MISSING_PROFILE:
        target[f'{path}_id'] = -1
    else:
        target[path] = user_company
