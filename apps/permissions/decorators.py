from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone


def _user_has_active_admin_role(user):
    """Rôle Admin ERP actif et non expiré (aligné sur UserRole du projet)."""
    from apps.permissions.models import UserRole

    return UserRole.objects.filter(
        user=user,
        is_active=True,
        role__name='Admin',
    ).exclude(
        expires_at__lt=timezone.now()
    ).exists()


def user_has_permission(user, permission_codename):
    """
    Vérifie si un utilisateur a une permission spécifique
    """
    if not getattr(user, 'is_authenticated', False):
        return False

    # Superuser Django ou rôle ERP « Admin » actif : accès complet API métier (RBAC).
    if getattr(user, 'is_superuser', False) or _user_has_active_admin_role(user):
        return True

    try:
        from apps.permissions.models import Permission, UserRole, RolePermission
        
        # Récupérer la permission
        permission = Permission.objects.get(codename=permission_codename, is_active=True)
        
        # Récupérer les rôles actifs de l'utilisateur
        user_roles = UserRole.objects.filter(
            user=user, 
            is_active=True
        ).exclude(
            expires_at__lt=timezone.now()
        ).values_list('role', flat=True)
        
        if not user_roles:
            return False
        
        # Vérifier si l'un des rôles de l'utilisateur a cette permission
        role_permission = RolePermission.objects.filter(
            role__in=user_roles,
            permission=permission,
            granted=True
        ).exists()
        
        return role_permission
        
    except Exception:
        return False


def require_permission(permission_codename):
    """
    Décorateur pour vérifier qu'un utilisateur a une permission spécifique
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Vérifier si l'utilisateur est authentifié
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Authentification requise',
                    'detail': 'Vous devez être connecté pour accéder à cette ressource'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Vérifier si l'utilisateur a la permission
            if not user_has_permission(request.user, permission_codename):
                return Response({
                    'error': 'Permission refusée',
                    'detail': f'Vous n\'avez pas la permission "{permission_codename}" pour effectuer cette action',
                    'required_permission': permission_codename
                }, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def user_has_any_permission(user, permission_codenames):
    """
    Vérifie si un utilisateur a au moins une des permissions spécifiées
    """
    for permission_codename in permission_codenames:
        if user_has_permission(user, permission_codename):
            return True
    return False


def user_has_all_permissions(user, permission_codenames):
    """
    Vérifie si un utilisateur a toutes les permissions spécifiées
    """
    for permission_codename in permission_codenames:
        if not user_has_permission(user, permission_codename):
            return False
    return True


def log_permission_check(user, permission_codename, granted, request=None):
    """
    Log la vérification d'une permission
    """
    from .models import PermissionLog
    
    try:
        permission = Permission.objects.get(codename=permission_codename)
        
        PermissionLog.objects.create(
            user=user,
            action='access_granted' if granted else 'access_denied',
            permission=permission,
            details={
                'permission_codename': permission_codename,
                'permission_name': permission.name,
                'endpoint': request.path if request else None,
                'method': request.method if request else None
            },
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
            user_agent=request.META.get('HTTP_USER_AGENT') if request else None
        )
    except Permission.DoesNotExist:
        pass
