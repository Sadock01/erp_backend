# Rôles métiers + matrice RolePermission (seul Admin gère users / RBAC / companies globales).

from django.db import migrations


SCOPED_ROLE_DEFAULTS = (
    {
        'name': 'Manager',
        'description': 'Inventaire, stock et ventes (sans gestion des utilisateurs ni RBAC).',
        'is_active': True,
        'is_system': True,
        'level': 1,
        'color': '#0d6efd',
        'icon': 'fas fa-user-tie',
    },
    {
        'name': 'Inventory Manager',
        'description': 'Catalogue produits, catégories et variantes.',
        'is_active': True,
        'is_system': True,
        'level': 1,
        'color': '#198754',
        'icon': 'fas fa-boxes',
    },
    {
        'name': 'Stock Manager',
        'description': 'Mouvements, ajustements et alertes de stock.',
        'is_active': True,
        'is_system': True,
        'level': 1,
        'color': '#fd7e14',
        'icon': 'fas fa-warehouse',
    },
    {
        'name': 'Sales Manager',
        'description': 'Commandes, factures, devis et paiements.',
        'is_active': True,
        'is_system': True,
        'level': 1,
        'color': '#20c997',
        'icon': 'fas fa-file-invoice-dollar',
    },
)


def forwards(apps, schema_editor):
    from apps.permissions.role_permission_policy import managed_role_names, role_grants_permission

    Role = apps.get_model('permissions', 'Role')
    Permission = apps.get_model('permissions', 'Permission')
    RolePermission = apps.get_model('permissions', 'RolePermission')

    for spec in SCOPED_ROLE_DEFAULTS:
        name = spec['name']
        defaults = {k: v for k, v in spec.items() if k != 'name'}
        Role.objects.update_or_create(name=name, defaults=defaults)

    names = managed_role_names()
    roles = {r.name: r for r in Role.objects.filter(name__in=names)}
    missing = set(names) - set(roles)
    if missing:
        raise RuntimeError(f"Rôles manquants après seed: {missing}")

    RolePermission.objects.filter(role__name__in=names).delete()

    to_create = []
    for perm in Permission.objects.filter(is_active=True).iterator():
        for role_name in names:
            if role_grants_permission(role_name, perm):
                to_create.append(
                    RolePermission(
                        role=roles[role_name],
                        permission=perm,
                        granted=True,
                        notes='permissions.0004 — matrice par rôle',
                    )
                )
    RolePermission.objects.bulk_create(to_create, batch_size=500)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_seed_permissions_and_role_bindings'),
    ]

    operations = [
        migrations.RunPython(forwards, noop_reverse),
    ]
