# Crée les lignes Permission, puis lie tout au rôle Admin et les actions « view » au rôle User.

from django.db import migrations


def seed_permissions_and_bindings(apps, schema_editor):
    from apps.permissions.permission_seed_data import iter_unique_permission_rows

    Permission = apps.get_model('permissions', 'Permission')
    Role = apps.get_model('permissions', 'Role')
    RolePermission = apps.get_model('permissions', 'RolePermission')

    for name, codename, app_label, action, resource in iter_unique_permission_rows():
        Permission.objects.update_or_create(
            codename=codename,
            defaults={
                'name': name,
                'description': f'Permission {codename}',
                'app_label': app_label,
                'action': action,
                'resource': resource,
                'is_active': True,
                'is_system': True,
            },
        )

    admin_role = Role.objects.filter(name='Admin').first()
    user_role = Role.objects.filter(name='User').first()
    if not admin_role or not user_role:
        raise RuntimeError(
            "Rôles Admin et User introuvables. Applique d'abord la migration 0002_seed_default_roles."
        )

    for perm in Permission.objects.filter(is_active=True):
        RolePermission.objects.update_or_create(
            role=admin_role,
            permission=perm,
            defaults={
                'granted': True,
                'notes': 'permissions.0003 — rôle Admin',
            },
        )

    # Utilisateur « standard » : uniquement les permissions d’action « view » (lecture).
    for perm in Permission.objects.filter(is_active=True, action='view'):
        RolePermission.objects.update_or_create(
            role=user_role,
            permission=perm,
            defaults={
                'granted': True,
                'notes': 'permissions.0003 — rôle User (lecture)',
            },
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_seed_default_roles'),
    ]

    operations = [
        migrations.RunPython(seed_permissions_and_bindings, noop_reverse),
    ]
