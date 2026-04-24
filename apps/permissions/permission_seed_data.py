"""
Définitions des permissions pour seed DB (migrations + scripts).
Aligné sur tests/setup_permissions + codenames utilisés dans les vues API.
"""

# (name, codename, app_label, action, resource)
PERMISSION_DEFINITIONS = (
    ('Voir le tableau de bord', 'dashboard_view', 'dashboard', 'view', 'dashboard'),
    ('Gérer le tableau de bord', 'dashboard_manage', 'dashboard', 'manage', 'dashboard'),
    ('Voir les produits', 'inventory_view', 'inventory', 'view', 'product'),
    ('Créer des produits', 'inventory_create', 'inventory', 'create', 'product'),
    ('Modifier des produits', 'inventory_update', 'inventory', 'update', 'product'),
    ('Supprimer des produits', 'inventory_delete', 'inventory', 'delete', 'product'),
    ('Gérer les produits', 'inventory_manage', 'inventory', 'manage', 'product'),
    ('Voir les catégories', 'inventory_category.view', 'inventory', 'view', 'category'),
    ('Créer des catégories', 'inventory_category.create', 'inventory', 'create', 'category'),
    ('Modifier des catégories', 'inventory_category.update', 'inventory', 'update', 'category'),
    ('Supprimer des catégories', 'inventory_category.delete', 'inventory', 'delete', 'category'),
    ('Gérer les catégories', 'inventory_category.manage', 'inventory', 'manage', 'category'),
    ('Voir les variants', 'inventory_variant.view', 'inventory', 'view', 'variant'),
    ('Créer des variants', 'inventory_variant.create', 'inventory', 'create', 'variant'),
    ('Modifier des variants', 'inventory_variant.update', 'inventory', 'update', 'variant'),
    ('Supprimer des variants', 'inventory_variant.delete', 'inventory', 'delete', 'variant'),
    ('Gérer les variants', 'inventory_variant.manage', 'inventory', 'manage', 'variant'),
    ('Voir le stock', 'stock_view', 'stock', 'view', 'stock'),
    ('Gérer le stock', 'stock_manage', 'stock', 'manage', 'stock'),
    ('Ajuster le stock', 'stock_adjust', 'stock', 'adjust', 'stock'),
    ('Voir les commandes', 'sales_order.view', 'sales', 'view', 'order'),
    ('Créer des commandes', 'sales_order.create', 'sales', 'create', 'order'),
    ('Modifier des commandes', 'sales_order.update', 'sales', 'update', 'order'),
    ('Supprimer des commandes', 'sales_order.delete', 'sales', 'delete', 'order'),
    ('Gérer les commandes', 'sales_order.manage', 'sales', 'manage', 'order'),
    ('Voir les factures', 'sales_invoice.view', 'sales', 'view', 'invoice'),
    ('Créer des factures', 'sales_invoice.create', 'sales', 'create', 'invoice'),
    ('Modifier des factures', 'sales_invoice.update', 'sales', 'update', 'invoice'),
    ('Supprimer des factures', 'sales_invoice.delete', 'sales', 'delete', 'invoice'),
    ('Gérer les factures', 'sales_invoice.manage', 'sales', 'manage', 'invoice'),
    ('Voir les clients', 'customers_view', 'customers', 'view', 'customer'),
    ('Créer des clients', 'customers_create', 'customers', 'create', 'customer'),
    ('Modifier des clients', 'customers_update', 'customers', 'update', 'customer'),
    ('Supprimer des clients', 'customers_delete', 'customers', 'delete', 'customer'),
    ('Gérer les clients', 'customers_manage', 'customers', 'manage', 'customer'),
    ('Voir les alertes', 'alerts_view', 'alerts', 'view', 'alert'),
    ('Créer des alertes', 'alerts_create', 'alerts', 'create', 'alert'),
    ('Modifier des alertes', 'alerts_update', 'alerts', 'update', 'alert'),
    ('Supprimer des alertes', 'alerts_delete', 'alerts', 'delete', 'alert'),
    ('Gérer les alertes', 'alerts_manage', 'alerts', 'manage', 'alert'),
    ('Voir les notifications', 'notifications_view', 'notifications', 'view', 'notification'),
    ('Créer des notifications', 'notifications_create', 'notifications', 'create', 'notification'),
    ('Modifier des notifications', 'notifications_update', 'notifications', 'update', 'notification'),
    ('Supprimer des notifications', 'notifications_delete', 'notifications', 'delete', 'notification'),
    ('Gérer les notifications', 'notifications_manage', 'notifications', 'manage', 'notification'),
    ('Voir les utilisateurs', 'users_view', 'users', 'view', 'user'),
    ('Créer des utilisateurs', 'users_create', 'users', 'create', 'user'),
    ('Modifier des utilisateurs', 'users_update', 'users', 'update', 'user'),
    ('Supprimer des utilisateurs', 'users_delete', 'users', 'delete', 'user'),
    ('Gérer les utilisateurs', 'users_manage', 'users', 'manage', 'user'),
    ('Voir les rôles', 'roles_view', 'roles', 'view', 'role'),
    ('Créer des rôles', 'roles_create', 'roles', 'create', 'role'),
    ('Modifier des rôles', 'roles_update', 'roles', 'update', 'role'),
    ('Supprimer des rôles', 'roles_delete', 'roles', 'delete', 'role'),
    ('Gérer les rôles', 'roles_manage', 'roles', 'manage', 'role'),
    ('Voir les permissions', 'permissions_view', 'permissions', 'view', 'permission'),
    ('Créer des permissions', 'permissions_create', 'permissions', 'create', 'permission'),
    ('Modifier des permissions', 'permissions_update', 'permissions', 'update', 'permission'),
    ('Supprimer des permissions', 'permissions_delete', 'permissions', 'delete', 'permission'),
    ('Gérer les permissions', 'permissions_manage', 'permissions', 'manage', 'permission'),
    # API permissions (apps/permissions/views.py, apps/common/views.py, apps/sales/views.py)
    ('Voir toutes les entreprises', 'companies_view_all', 'companies', 'view', 'company_all'),
    ('Voir les rôles RBAC', 'permissions_roles_view', 'permissions', 'view', 'roles_rbac'),
    ('Gérer les rôles RBAC', 'permissions_roles_manage', 'permissions', 'manage', 'roles_rbac'),
    ('Voir les permissions RBAC', 'permissions_permissions_view', 'permissions', 'view', 'permissions_rbac'),
    ('Gérer les permissions RBAC', 'permissions_permissions_manage', 'permissions', 'manage', 'permissions_rbac'),
    ('Voir les user-roles RBAC', 'permissions_user_roles_view', 'permissions', 'view', 'user_roles_rbac'),
    ('Gérer les user-roles RBAC', 'permissions_user_roles_manage', 'permissions', 'manage', 'user_roles_rbac'),
    ('Voir les logs permissions', 'permissions_logs_view', 'permissions', 'view', 'permission_logs'),
    ('Voir les stats permissions', 'permissions_stats_view', 'permissions', 'view', 'permission_stats'),
    ('Créer commandes (alias vues)', 'sales_orders_create', 'sales', 'create', 'orders'),
    ('Voir factures (alias vues)', 'sales_invoices_view', 'sales', 'view', 'invoices'),
    ('Créer factures (alias vues)', 'sales_invoices_create', 'sales', 'create', 'invoices'),
    ('Voir devis', 'sales_proformas_view', 'sales', 'view', 'proformas'),
    ('Créer devis', 'sales_proformas_create', 'sales', 'create', 'proformas'),
    ('Voir paiements', 'sales_payments_view', 'sales', 'view', 'payments'),
    ('Créer paiements', 'sales_payments_create', 'sales', 'create', 'payments'),
)


def iter_unique_permission_rows():
    """Itère les lignes en dédoublonnant par codename."""
    seen = set()
    for row in PERMISSION_DEFINITIONS:
        codename = row[1]
        if codename in seen:
            continue
        seen.add(codename)
        yield row
