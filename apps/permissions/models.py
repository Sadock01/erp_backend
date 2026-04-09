from django.db import models
from django.contrib.auth.models import User
from apps.common.models import BaseModel


class Role(BaseModel):
    """
    Modèle pour les rôles des utilisateurs
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom du rôle",
        help_text="Nom unique du rôle (ex: Admin, Manager, Sales)"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée du rôle",
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le rôle est actif"
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="Rôle système",
        help_text="Rôles système qui ne peuvent pas être supprimés"
    )
    level = models.PositiveIntegerField(
        default=0,
        verbose_name="Niveau hiérarchique",
        help_text="Niveau hiérarchique (0=Admin, 1=Manager, 2=User, 3=Viewer)"
    )
    color = models.CharField(
        max_length=7,
        default="#007bff",
        verbose_name="Couleur",
        help_text="Couleur hexadécimale pour l'affichage (ex: #007bff)"
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Icône",
        help_text="Classe CSS de l'icône (ex: fas fa-user-shield)"
    )

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['level', 'name']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['level']),
            models.Index(fields=['is_system']),
        ]

    def __str__(self):
        return self.name

    @property
    def user_count(self):
        """Retourne le nombre d'utilisateurs ayant ce rôle"""
        return self.userrole_set.filter(is_active=True).count()

    @property
    def permission_count(self):
        """Retourne le nombre de permissions accordées"""
        return self.rolepermission_set.filter(granted=True).count()


class Permission(BaseModel):
    """
    Modèle pour les permissions granulaires
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nom de la permission",
        help_text="Nom lisible de la permission (ex: Voir les clients)"
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Code de la permission",
        help_text="Code unique de la permission (ex: customers_view)"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Description détaillée de la permission",
        blank=True,
        null=True
    )
    app_label = models.CharField(
        max_length=50,
        verbose_name="Application",
        help_text="Nom de l'application (ex: customers, sales, inventory)"
    )
    action = models.CharField(
        max_length=20,
        verbose_name="Action",
        help_text="Type d'action (ex: view, create, update, delete, manage)"
    )
    resource = models.CharField(
        max_length=50,
        verbose_name="Ressource",
        help_text="Ressource concernée (ex: customer, order, product, stock)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si la permission est active"
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name="Permission système",
        help_text="Permissions système qui ne peuvent pas être supprimées"
    )

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['app_label', 'resource', 'action']
        unique_together = ['app_label', 'resource', 'action']
        indexes = [
            models.Index(fields=['app_label']),
            models.Index(fields=['action']),
            models.Index(fields=['resource']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.app_label}.{self.resource}.{self.action}"

    @property
    def full_codename(self):
        """Retourne le code complet de la permission"""
        return f"{self.app_label}.{self.resource}.{self.action}"


class RolePermission(BaseModel):
    """
    Modèle de liaison entre les rôles et les permissions
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="Rôle",
        help_text="Rôle concerné"
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name="Permission",
        help_text="Permission concernée"
    )
    granted = models.BooleanField(
        default=True,
        verbose_name="Accordée",
        help_text="Indique si la permission est accordée ou refusée"
    )
    conditions = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Conditions",
        help_text="Conditions spéciales pour cette permission (JSON)"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur cette attribution de permission"
    )

    class Meta:
        verbose_name = "Permission de rôle"
        verbose_name_plural = "Permissions de rôles"
        unique_together = ['role', 'permission']
        ordering = ['role', 'permission']

    def __str__(self):
        status = "✓" if self.granted else "✗"
        return f"{self.role.name} {status} {self.permission.name}"


class UserRole(BaseModel):
    """
    Modèle de liaison entre les utilisateurs et les rôles
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        help_text="Utilisateur concerné"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        verbose_name="Rôle",
        help_text="Rôle assigné"
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name="Assigné par",
        help_text="Utilisateur qui a assigné ce rôle"
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Assigné le",
        help_text="Date d'assignation du rôle"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Expire le",
        help_text="Date d'expiration du rôle (optionnel)"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si l'assignation est active"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur cette assignation de rôle"
    )

    class Meta:
        verbose_name = "Rôle d'utilisateur"
        verbose_name_plural = "Rôles d'utilisateurs"
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"

    @property
    def is_expired(self):
        """Vérifie si le rôle a expiré"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False

    @property
    def days_until_expiry(self):
        """Retourne le nombre de jours avant expiration"""
        if self.expires_at:
            from django.utils import timezone
            delta = self.expires_at - timezone.now()
            return delta.days
        return None


class PermissionLog(BaseModel):
    """
    Modèle pour logger les actions de permissions
    """
    ACTION_CHOICES = [
        ('role_assigned', 'Rôle assigné'),
        ('role_removed', 'Rôle retiré'),
        ('permission_granted', 'Permission accordée'),
        ('permission_revoked', 'Permission révoquée'),
        ('access_denied', 'Accès refusé'),
        ('access_granted', 'Accès accordé'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Utilisateur",
        help_text="Utilisateur concerné par l'action"
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name="Action",
        help_text="Type d'action effectuée"
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='permission_logs_target',
        verbose_name="Utilisateur cible",
        help_text="Utilisateur cible de l'action"
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Rôle",
        help_text="Rôle concerné par l'action"
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Permission",
        help_text="Permission concernée par l'action"
    )
    details = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Détails",
        help_text="Détails supplémentaires de l'action (JSON)"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Adresse IP",
        help_text="Adresse IP de l'utilisateur"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        verbose_name="User Agent",
        help_text="User Agent du navigateur"
    )

    class Meta:
        verbose_name = "Log de permission"
        verbose_name_plural = "Logs de permissions"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['target_user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_action_display()} - {self.user} - {self.created_at}"