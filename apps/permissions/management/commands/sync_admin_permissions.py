from django.core.management.base import BaseCommand

from apps.permissions.models import Permission, Role, RolePermission


class Command(BaseCommand):
    help = (
        'Accorde toutes les permissions actives au rôle ERP Admin '
        '(RolePermission avec granted=True). Utile après import ou si la liste membres / RBAC est incohérente.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            default='Admin',
            help='Nom du rôle ERP (défaut: Admin)',
        )

    def handle(self, *args, **options):
        role_name = options['role']
        role, _ = Role.objects.get_or_create(
            name=role_name,
            defaults={
                'description': 'Administrateur',
                'is_active': True,
                'level': 0,
            },
        )
        perms = Permission.objects.filter(is_active=True)
        created_count = 0
        for p in perms:
            _, created = RolePermission.objects.update_or_create(
                role=role,
                permission=p,
                defaults={'granted': True},
            )
            if created:
                created_count += 1
        total = RolePermission.objects.filter(role=role, granted=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Rôle « {role_name} » : {total} permissions accordées '
                f'({created_count} liaisons créées, les autres mises à jour si besoin).'
            )
        )
