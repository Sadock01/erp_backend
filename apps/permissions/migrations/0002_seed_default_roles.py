# Données initiales : rôles système requis par l’API (inscription, invitation, RBAC).

from django.db import migrations


DEFAULT_ROLES = (
    {
        'name': 'Admin',
        'description': 'Administrateur de l’entreprise (accès complet application).',
        'is_active': True,
        'is_system': True,
        'level': 0,
        'color': '#dc3545',
        'icon': 'fas fa-user-shield',
    },
    {
        'name': 'User',
        'description': 'Utilisateur standard (droits selon les permissions du rôle).',
        'is_active': True,
        'is_system': True,
        'level': 2,
        'color': '#6c757d',
        'icon': 'fas fa-user',
    },
)


def seed_default_roles(apps, schema_editor):
    Role = apps.get_model('permissions', 'Role')
    for spec in DEFAULT_ROLES:
        name = spec['name']
        defaults = {k: v for k, v in spec.items() if k != 'name'}
        Role.objects.update_or_create(name=name, defaults=defaults)


def noop_reverse(apps, schema_editor):
    """On ne supprime pas les rôles au rollback (UserRole pourrait référencer)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_default_roles, noop_reverse),
    ]
