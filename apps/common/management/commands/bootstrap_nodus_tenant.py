from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.common.erp_wipe import wipe_all_erp_tenant_data
from apps.common.models import Company, UserProfile
from apps.permissions.models import Role, UserRole


class Command(BaseCommand):
    help = (
        'Crée une entreprise « Nodus » (ou nom choisi) et un utilisateur boutique '
        '(rôle ERP Admin, non superuser) lié par UserProfile. '
        'Avec --fresh, supprime toutes les données multi-tenant et les utilisateurs '
        'non superuser avant (base vide pour ta boutique).'
    )

    def add_arguments(self, parser):
        parser.add_argument('--email', default='boutique@nodus.local', help='Email / username Django')
        parser.add_argument('--password', default='changeme', help='Mot de passe initial')
        parser.add_argument('--company', default='Nodus', help='Nom de l’entreprise')
        parser.add_argument(
            '--fresh',
            action='store_true',
            help=(
                'DANGER : supprime toutes les lignes UserRole, toutes les Company '
                '(cascade : clients, commandes, produits, profils, etc.) et tous les '
                'User non superuser, puis recrée uniquement l’entreprise et le compte demandés.'
            ),
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        password = options['password']
        company_name = options['company'].strip()
        fresh = options['fresh']

        if fresh:
            self.stdout.write(self.style.WARNING('Mode --fresh : suppression des données ERP existantes…'))
            wipe_all_erp_tenant_data()
            self.stdout.write('  → Données métier, profils, rôles et entreprises supprimés (ordre PROTECT/CASCADE).')
            User = get_user_model()
            deleted_users, _ = User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f'  → {deleted_users} enregistrements liés aux utilisateurs (non superuser) supprimés.')

        company, _ = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'email': email,
                'is_active': True,
                'primary_color': '#007bff',
                'description': 'Boutique Nodus',
            },
        )

        User = get_user_model()
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email,
                'first_name': 'Admin',
                'last_name': 'Boutique',
                'is_active': True,
                'is_staff': False,
                'is_superuser': False,
            },
        )
        if not created and user.username != email:
            user.username = email
        user.set_password(password)
        user.is_superuser = False
        user.is_staff = False
        user.save()

        UserProfile.objects.update_or_create(
            user=user,
            defaults={'company': company, 'is_company_admin': True},
        )

        admin_role, _ = Role.objects.get_or_create(
            name='Admin',
            defaults={
                'description': 'Administrateur',
                'is_active': True,
                'level': 0,
            },
        )
        UserRole.objects.update_or_create(
            user=user,
            role=admin_role,
            defaults={'is_active': True},
        )

        call_command('sync_admin_permissions')

        self.stdout.write(
            self.style.SUCCESS(
                f'Terminé — Entreprise « {company.name} » (id={company.id}), '
                f'compte {email} (Admin ERP, pas superuser). '
                f'Tu ne vois que cette société dans l’API ; un superuser Django voit encore tout.'
            )
        )
