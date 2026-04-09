from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Role, Permission, RolePermission, UserRole, PermissionLog
from .serializers import (
    RoleSerializer, RoleListSerializer, PermissionSerializer, PermissionListSerializer,
    UserRoleSerializer, UserRoleCreateSerializer, PermissionLogSerializer,
    UserPermissionsSerializer, RolePermissionsSerializer, AssignRoleSerializer,
    GrantPermissionSerializer, BulkAssignRoleSerializer, PermissionStatsSerializer,
    UserSerializer, UserCreateSerializer, UserListSerializer
)
from .decorators import user_has_permission


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def test_endpoint(request):
    """
    Endpoint de test pour vérifier que l'API Permissions fonctionne
    """
    if request.method == 'GET':
        return Response({
            'message': 'API Permissions fonctionne correctement !',
            'endpoints': [
                'GET /api/permissions/roles/ - Lister les rôles',
                'POST /api/permissions/roles/ - Créer un rôle',
                'GET /api/permissions/permissions/ - Lister les permissions',
                'GET /api/permissions/user-roles/ - Lister les rôles d\'utilisateurs',
                'POST /api/permissions/user-roles/ - Assigner un rôle',
                'GET /api/permissions/logs/ - Lister les logs de permissions',
                'GET /api/permissions/stats/ - Statistiques des permissions'
            ]
        })
    elif request.method == 'POST':
        return Response({
            'message': 'API Permissions fonctionne !',
            'method': 'POST',
            'data_received': request.data,
            'status': 'success'
        })


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des rôles - SÉCURISÉ
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['is_active', 'is_system', 'level']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'level', 'created_at']
    ordering = ['level', 'name']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer

    def list(self, request, *args, **kwargs):
        """Lister les rôles - Nécessite permissions_roles_view"""
        if not user_has_permission(request.user, 'permissions_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles',
                'required_permission': 'permissions_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un rôle - Nécessite permissions_roles_manage"""
        if not user_has_permission(request.user, 'permissions_roles_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des rôles',
                'required_permission': 'permissions_roles_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un rôle - Nécessite permissions_roles_view"""
        if not user_has_permission(request.user, 'permissions_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles',
                'required_permission': 'permissions_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un rôle - Nécessite permissions_roles_manage"""
        if not user_has_permission(request.user, 'permissions_roles_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les rôles',
                'required_permission': 'permissions_roles_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un rôle - Nécessite permissions_roles_manage"""
        if not user_has_permission(request.user, 'permissions_roles_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les rôles',
                'required_permission': 'permissions_roles_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lister uniquement les rôles actifs - Nécessite permissions_roles_view"""
        if not user_has_permission(request.user, 'permissions_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles',
                'required_permission': 'permissions_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_roles = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_roles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def system(self, request):
        """Lister uniquement les rôles système - Nécessite permissions_roles_view"""
        if not user_has_permission(request.user, 'permissions_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles',
                'required_permission': 'permissions_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        system_roles = self.get_queryset().filter(is_system=True)
        serializer = self.get_serializer(system_roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Lister les permissions d'un rôle - Nécessite permissions_roles_view"""
        if not user_has_permission(request.user, 'permissions_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles',
                'required_permission': 'permissions_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        role = self.get_object()
        role_permissions = RolePermission.objects.filter(role=role)
        
        granted_permissions = role_permissions.filter(granted=True).values_list('permission', flat=True)
        denied_permissions = role_permissions.filter(granted=False).values_list('permission', flat=True)
        
        permissions = Permission.objects.filter(
            Q(id__in=granted_permissions) | Q(id__in=denied_permissions)
        ).distinct()
        
        granted_perms = permissions.filter(id__in=granted_permissions)
        denied_perms = permissions.filter(id__in=denied_permissions)
        
        serializer = RolePermissionsSerializer({
            'role': role,
            'permissions': permissions,
            'granted_permissions': granted_perms,
            'denied_permissions': denied_perms,
            'total_permissions': permissions.count()
        })
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des permissions - SÉCURISÉ
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['is_active', 'is_system', 'app_label', 'action', 'resource']
    search_fields = ['name', 'codename', 'description']
    ordering_fields = ['name', 'app_label', 'action', 'resource']
    ordering = ['app_label', 'resource', 'action']

    def get_serializer_class(self):
        if self.action == 'list':
            return PermissionListSerializer
        return PermissionSerializer

    def list(self, request, *args, **kwargs):
        """Lister les permissions - Nécessite permissions_permissions_view"""
        if not user_has_permission(request.user, 'permissions_permissions_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les permissions',
                'required_permission': 'permissions_permissions_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer une permission - Nécessite permissions_permissions_manage"""
        if not user_has_permission(request.user, 'permissions_permissions_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des permissions',
                'required_permission': 'permissions_permissions_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir une permission - Nécessite permissions_permissions_view"""
        if not user_has_permission(request.user, 'permissions_permissions_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les permissions',
                'required_permission': 'permissions_permissions_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier une permission - Nécessite permissions_permissions_manage"""
        if not user_has_permission(request.user, 'permissions_permissions_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les permissions',
                'required_permission': 'permissions_permissions_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer une permission - Nécessite permissions_permissions_manage"""
        if not user_has_permission(request.user, 'permissions_permissions_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les permissions',
                'required_permission': 'permissions_permissions_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def by_app(self, request):
        """Lister les permissions par application - Nécessite permissions_permissions_view"""
        if not user_has_permission(request.user, 'permissions_permissions_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les permissions',
                'required_permission': 'permissions_permissions_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        app_label = request.query_params.get('app', '')
        if app_label:
            permissions = self.get_queryset().filter(app_label=app_label)
        else:
            permissions = self.get_queryset()
        
        # Grouper par application
        apps = {}
        for perm in permissions:
            if perm.app_label not in apps:
                apps[perm.app_label] = []
            apps[perm.app_label].append(PermissionListSerializer(perm).data)
        
        return Response(apps)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lister uniquement les permissions actives - Nécessite permissions_permissions_view"""
        if not user_has_permission(request.user, 'permissions_permissions_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les permissions',
                'required_permission': 'permissions_permissions_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_permissions = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_permissions, many=True)
        return Response(serializer.data)


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des rôles d'utilisateurs - SÉCURISÉ
    """
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['is_active', 'role', 'user', 'assigned_by']
    search_fields = ['user__username', 'user__email', 'role__name', 'notes']
    ordering_fields = ['assigned_at', 'expires_at', 'created_at']
    ordering = ['-assigned_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRoleCreateSerializer
        return UserRoleSerializer

    def list(self, request, *args, **kwargs):
        """Lister les rôles utilisateurs - Nécessite permissions_user_roles_view"""
        if not user_has_permission(request.user, 'permissions_user_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un rôle utilisateur - Nécessite permissions_user_roles_manage"""
        if not user_has_permission(request.user, 'permissions_user_roles_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un rôle utilisateur - Nécessite permissions_user_roles_view"""
        if not user_has_permission(request.user, 'permissions_user_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un rôle utilisateur - Nécessite permissions_user_roles_manage"""
        if not user_has_permission(request.user, 'permissions_user_roles_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un rôle utilisateur - Nécessite permissions_user_roles_manage"""
        if not user_has_permission(request.user, 'permissions_user_roles_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lister uniquement les rôles actifs - Nécessite permissions_user_roles_view"""
        if not user_has_permission(request.user, 'permissions_user_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_roles = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_roles, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Lister les rôles expirés - Nécessite permissions_user_roles_view"""
        if not user_has_permission(request.user, 'permissions_user_roles_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les rôles utilisateurs',
                'required_permission': 'permissions_user_roles_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        expired_roles = self.get_queryset().filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        serializer = self.get_serializer(expired_roles, many=True)
        return Response(serializer.data)


class PermissionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les logs de permissions - SÉCURISÉ
    """
    queryset = PermissionLog.objects.all()
    serializer_class = PermissionLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['action', 'user', 'target_user', 'role', 'permission']
    search_fields = ['user__username', 'target_user__username', 'role__name', 'permission__name']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']

    def list(self, request, *args, **kwargs):
        """Lister les logs - Nécessite permissions_logs_view"""
        if not user_has_permission(request.user, 'permissions_logs_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les logs de permissions',
                'required_permission': 'permissions_logs_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un log - Nécessite permissions_logs_view"""
        if not user_has_permission(request.user, 'permissions_logs_view'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les logs de permissions',
                'required_permission': 'permissions_logs_view'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_permissions(request, user_id):
    """
    Récupérer les permissions d'un utilisateur - Nécessite permissions_user_roles_view
    """
    if not user_has_permission(request.user, 'permissions_user_roles_view'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de voir les rôles utilisateurs',
            'required_permission': 'permissions_user_roles_view'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    # Récupérer les rôles actifs de l'utilisateur
    user_roles = UserRole.objects.filter(user=user, is_active=True)
    roles = [ur.role for ur in user_roles if not ur.is_expired]
    
    # Récupérer les permissions accordées
    role_permissions = RolePermission.objects.filter(
        role__in=roles,
        granted=True
    ).values_list('permission', flat=True)
    
    permissions = Permission.objects.filter(id__in=role_permissions, is_active=True)
    
    serializer = UserPermissionsSerializer({
        'user': user,
        'roles': roles,
        'permissions': permissions,
        'total_permissions': permissions.count(),
        'total_roles': len(roles)
    })
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def permission_stats(request):
    """
    Récupérer les statistiques des permissions - Nécessite permissions_stats_view
    """
    if not user_has_permission(request.user, 'permissions_stats_view'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de voir les statistiques de permissions',
            'required_permission': 'permissions_stats_view'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Statistiques de base
    total_users = User.objects.count()
    total_roles = Role.objects.count()
    total_permissions = Permission.objects.count()
    active_roles = Role.objects.filter(is_active=True).count()
    system_roles = Role.objects.filter(is_system=True).count()
    
    # Utilisateurs par rôle
    users_by_role = {}
    for role in Role.objects.all():
        count = UserRole.objects.filter(role=role, is_active=True).count()
        users_by_role[role.name] = count
    
    # Permissions par application
    permissions_by_app = {}
    for perm in Permission.objects.all():
        if perm.app_label not in permissions_by_app:
            permissions_by_app[perm.app_label] = 0
        permissions_by_app[perm.app_label] += 1
    
    # Assignations récentes
    recent_assignments = UserRole.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-created_at')[:10]
    
    # Logs récents
    recent_logs = PermissionLog.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-created_at')[:10]
    
    serializer = PermissionStatsSerializer({
        'total_users': total_users,
        'total_roles': total_roles,
        'total_permissions': total_permissions,
        'active_roles': active_roles,
        'system_roles': system_roles,
        'users_by_role': users_by_role,
        'permissions_by_app': permissions_by_app,
        'recent_assignments': recent_assignments,
        'recent_logs': recent_logs
    })
    
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des utilisateurs par les admins - SÉCURISÉ
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    filterset_fields = ['is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['username']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'list':
            return UserListSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        """Lister les utilisateurs - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Créer un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de créer des utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Voir un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Modifier un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de modifier les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Supprimer un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de supprimer les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Lister uniquement les utilisateurs actifs - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        active_users = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def staff(self, request):
        """Lister uniquement les utilisateurs staff - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        staff_users = self.get_queryset().filter(is_staff=True)
        serializer = self.get_serializer(staff_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activer un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.is_active = True
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Désactiver un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user.is_active = False
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        """Réinitialiser le mot de passe d'un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password:
            return Response({
                'error': 'Nouveau mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Mot de passe réinitialisé avec succès'
        })

    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """Lister les rôles d'un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        user_roles = UserRole.objects.filter(user=user, is_active=True)
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Assigner un rôle à un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        role_id = request.data.get('role_id')
        expires_at = request.data.get('expires_at')
        notes = request.data.get('notes', '')
        
        if not role_id:
            return Response({
                'error': 'ID du rôle requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({
                'error': 'Rôle introuvable'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Vérifier si l'utilisateur a déjà ce rôle
        existing_role = UserRole.objects.filter(user=user, role=role).first()
        if existing_role:
            if existing_role.is_active:
                return Response({
                    'error': 'L\'utilisateur a déjà ce rôle'
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Réactiver le rôle existant
                existing_role.is_active = True
                existing_role.assigned_by = request.user
                existing_role.assigned_at = timezone.now()
                existing_role.expires_at = expires_at
                existing_role.notes = notes
                existing_role.save()
                serializer = UserRoleSerializer(existing_role)
                return Response(serializer.data)
        
        # Créer un nouveau rôle
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            assigned_by=request.user,
            expires_at=expires_at,
            notes=notes,
            is_active=True
        )
        
        serializer = UserRoleSerializer(user_role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_role(self, request, pk=None):
        """Retirer un rôle d'un utilisateur - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de gérer les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response({
                'error': 'ID du rôle requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_role = UserRole.objects.get(user=user, role_id=role_id, is_active=True)
        except UserRole.DoesNotExist:
            return Response({
                'error': 'Rôle non trouvé pour cet utilisateur'
            }, status=status.HTTP_404_NOT_FOUND)
        
        user_role.is_active = False
        user_role.save()
        
        return Response({
            'message': 'Rôle retiré avec succès'
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Résumé des utilisateurs - Nécessite users_manage"""
        if not user_has_permission(request.user, 'users_manage'):
            return Response({
                'error': 'Permission refusée',
                'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
                'required_permission': 'users_manage'
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.get_queryset()
        
        # Statistiques générales
        total_users = queryset.count()
        active_users = queryset.filter(is_active=True).count()
        inactive_users = queryset.filter(is_active=False).count()
        staff_users = queryset.filter(is_staff=True).count()
        superusers = queryset.filter(is_superuser=True).count()
        
        # Utilisateurs récents (7 derniers jours)
        week_ago = timezone.now() - timezone.timedelta(days=7)
        recent_users = queryset.filter(date_joined__gte=week_ago).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'staff_users': staff_users,
            'superusers': superusers,
            'recent_users': recent_users,
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def admin_create_user_with_roles(request):
    """
    Créer un utilisateur avec des rôles spécifiques - Nécessite users_manage
    """
    if not user_has_permission(request.user, 'users_manage'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de créer des utilisateurs',
            'required_permission': 'users_manage'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = UserCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'message': 'Utilisateur créé avec succès'
        }, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_assign_roles_to_users(request):
    """
    Assigner un rôle à plusieurs utilisateurs - Nécessite users_manage
    """
    if not user_has_permission(request.user, 'users_manage'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de gérer les utilisateurs',
            'required_permission': 'users_manage'
        }, status=status.HTTP_403_FORBIDDEN)
    
    user_ids = request.data.get('user_ids', [])
    role_id = request.data.get('role_id')
    expires_at = request.data.get('expires_at')
    notes = request.data.get('notes', '')
    
    if not user_ids or not role_id:
        return Response({
            'error': 'IDs des utilisateurs et ID du rôle requis'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        role = Role.objects.get(id=role_id)
    except Role.DoesNotExist:
        return Response({
            'error': 'Rôle introuvable'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier que tous les utilisateurs existent
    users = User.objects.filter(id__in=user_ids)
    if users.count() != len(user_ids):
        return Response({
            'error': 'Certains utilisateurs n\'existent pas'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    assigned_count = 0
    errors = []
    
    for user in users:
        # Vérifier si l'utilisateur a déjà ce rôle
        existing_role = UserRole.objects.filter(user=user, role=role).first()
        if existing_role:
            if existing_role.is_active:
                errors.append(f'L\'utilisateur {user.username} a déjà ce rôle')
                continue
            else:
                # Réactiver le rôle existant
                existing_role.is_active = True
                existing_role.assigned_by = request.user
                existing_role.assigned_at = timezone.now()
                existing_role.expires_at = expires_at
                existing_role.notes = notes
                existing_role.save()
                assigned_count += 1
        else:
            # Créer un nouveau rôle
            UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=request.user,
                expires_at=expires_at,
                notes=notes,
                is_active=True
            )
            assigned_count += 1
    
    return Response({
        'message': f'Rôle assigné à {assigned_count} utilisateur(s)',
        'assigned_count': assigned_count,
        'errors': errors
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detailed_permissions(request, user_id):
    """
    Récupérer les permissions détaillées d'un utilisateur - Nécessite users_manage
    """
    if not user_has_permission(request.user, 'users_manage'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de voir les utilisateurs',
            'required_permission': 'users_manage'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Utilisateur introuvable'}, status=status.HTTP_404_NOT_FOUND)
    
    # Récupérer les rôles actifs de l'utilisateur
    user_roles = UserRole.objects.filter(user=user, is_active=True)
    roles = [ur.role for ur in user_roles if not ur.is_expired]
    
    # Récupérer les permissions accordées et refusées
    role_permissions = RolePermission.objects.filter(role__in=roles)
    
    granted_permissions = role_permissions.filter(granted=True).values_list('permission', flat=True)
    denied_permissions = role_permissions.filter(granted=False).values_list('permission', flat=True)
    
    granted_perms = Permission.objects.filter(id__in=granted_permissions, is_active=True)
    denied_perms = Permission.objects.filter(id__in=denied_permissions, is_active=True)
    
    # Grouper par application
    permissions_by_app = {}
    for perm in granted_perms:
        if perm.app_label not in permissions_by_app:
            permissions_by_app[perm.app_label] = {'granted': [], 'denied': []}
        permissions_by_app[perm.app_label]['granted'].append({
            'id': perm.id,
            'name': perm.name,
            'codename': perm.codename,
            'action': perm.action,
            'resource': perm.resource
        })
    
    for perm in denied_perms:
        if perm.app_label not in permissions_by_app:
            permissions_by_app[perm.app_label] = {'granted': [], 'denied': []}
        permissions_by_app[perm.app_label]['denied'].append({
            'id': perm.id,
            'name': perm.name,
            'codename': perm.codename,
            'action': perm.action,
            'resource': perm.resource
        })
    
    return Response({
        'user': UserSerializer(user).data,
        'roles': RoleListSerializer(roles, many=True).data,
        'permissions_by_app': permissions_by_app,
        'total_granted': granted_perms.count(),
        'total_denied': denied_perms.count(),
        'total_roles': len(roles)
    })