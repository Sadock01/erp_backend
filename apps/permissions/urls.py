from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configuration du router pour les ViewSets
router = DefaultRouter()
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'user-roles', views.UserRoleViewSet, basename='userrole')
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'logs', views.PermissionLogViewSet, basename='permissionlog')

urlpatterns = [
    # Inclusion des routes du router
    path('', include(router.urls)),
    
    # Endpoint de test
    path('test/', views.test_endpoint, name='test'),
    
    # Endpoints spéciaux
    path('user-permissions/<int:user_id>/', views.user_permissions, name='user_permissions'),
    path('stats/', views.permission_stats, name='permission_stats'),
    
    # Endpoints pour la gestion des utilisateurs par admin
    path('admin/create-user/', views.admin_create_user_with_roles, name='admin_create_user'),
    path('admin/bulk-assign-roles/', views.bulk_assign_roles_to_users, name='bulk_assign_roles'),
    path('admin/user-permissions/<int:user_id>/', views.user_detailed_permissions, name='user_detailed_permissions'),
]
