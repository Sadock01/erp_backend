from django.db import models
from django.utils import timezone
from datetime import timedelta
import random
import string


class BaseModel(models.Model):
    """
    Modèle de base avec des champs communs
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date de création de l'enregistrement"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification",
        help_text="Date de dernière modification"
    )

    class Meta:
        abstract = True


class Company(BaseModel):
    """
    Modèle pour les informations de l'entreprise utilisant le logiciel ERP
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Nom de l'entreprise",
        help_text="Nom officiel de l'entreprise"
    )
    logo = models.ImageField(
        upload_to='companies/logos/',
        blank=True,
        null=True,
        verbose_name="Logo",
        help_text="Logo de l'entreprise"
    )
    primary_color = models.CharField(
        max_length=7,
        default='#007bff',
        verbose_name="Couleur principale",
        help_text="Couleur principale de l'entreprise (format hexadécimal, ex: #007bff)"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de l'entreprise"
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Email de contact",
        help_text="Adresse email principale de l'entreprise"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone",
        help_text="Numéro de téléphone principal"
    )
    address = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adresse",
        help_text="Adresse complète de l'entreprise"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ville",
        help_text="Ville de l'entreprise"
    )
    postal_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="Code postal",
        help_text="Code postal de l'entreprise"
    )
    country = models.CharField(
        max_length=100,
        default="France",
        verbose_name="Pays",
        help_text="Pays de l'entreprise"
    )
    website = models.URLField(
        blank=True,
        null=True,
        verbose_name="Site web",
        help_text="Site web de l'entreprise"
    )
    tax_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro de TVA",
        help_text="Numéro de TVA intracommunautaire"
    )
    registration_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Numéro d'enregistrement",
        help_text="Numéro SIRET ou équivalent"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si l'entreprise est active"
    )
    settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Paramètres",
        help_text="Paramètres personnalisés de l'entreprise"
    )

    class Meta:
        verbose_name = "Entreprise"
        verbose_name_plural = "Entreprises"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Retourne l'adresse complète formatée"""
        address_parts = []
        if self.address:
            address_parts.append(self.address)
        if self.postal_code and self.city:
            address_parts.append(f"{self.postal_code} {self.city}")
        if self.country:
            address_parts.append(self.country)
        return ", ".join(address_parts)

    def get_setting(self, key, default=None):
        """Récupère un paramètre spécifique"""
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        """Définit un paramètre spécifique"""
        if not self.settings:
            self.settings = {}
        self.settings[key] = value
        self.save()


class UserProfile(BaseModel):
    """
    Modèle pour étendre les informations utilisateur avec la relation à l'entreprise
    """
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        help_text="Utilisateur associé"
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise de l'utilisateur"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone personnel",
        help_text="Numéro de téléphone personnel de l'utilisateur"
    )
    position = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Poste",
        help_text="Poste occupé dans l'entreprise"
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Département",
        help_text="Département de l'utilisateur"
    )
    hire_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date d'embauche",
        help_text="Date d'embauche dans l'entreprise"
    )
    is_company_admin = models.BooleanField(
        default=False,
        verbose_name="Admin de l'entreprise",
        help_text="Indique si l'utilisateur est administrateur de l'entreprise"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur l'utilisateur"
    )

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        ordering = ['user__last_name', 'user__first_name']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['is_company_admin']),
            models.Index(fields=['hire_date']),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.company.name}"

    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return self.user.get_full_name()

    @property
    def email(self):
        """Retourne l'email de l'utilisateur"""
        return self.user.email

    def get_company_users(self):
        """Retourne tous les utilisateurs de la même entreprise"""
        return UserProfile.objects.filter(company=self.company).exclude(id=self.id)


class PasswordResetCode(models.Model):
    """
    Modèle pour stocker les codes de reset de mot de passe
    """
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        help_text="Utilisateur concerné par le reset"
    )
    email = models.EmailField(
        verbose_name="Email",
        help_text="Email de l'utilisateur"
    )
    code = models.CharField(
        max_length=6,
        verbose_name="Code de vérification",
        help_text="Code de 6 chiffres"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
        help_text="Date de création du code"
    )
    expires_at = models.DateTimeField(
        verbose_name="Date d'expiration",
        help_text="Date d'expiration du code"
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Utilisé",
        help_text="Indique si le code a été utilisé"
    )
    attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Tentatives",
        help_text="Nombre de tentatives de validation"
    )

    class Meta:
        verbose_name = "Code de reset de mot de passe"
        verbose_name_plural = "Codes de reset de mot de passe"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'code']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Code pour {self.email} - {self.code}"

    def save(self, *args, **kwargs):
        """Générer le code et définir l'expiration"""
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)  # 15 minutes
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        """Générer un code de 6 chiffres"""
        return ''.join(random.choices(string.digits, k=6))

    def is_valid(self):
        """Vérifier si le code est valide"""
        return (
            not self.is_used and
            self.attempts < 3 and
            timezone.now() < self.expires_at
        )

    def mark_as_used(self):
        """Marquer le code comme utilisé"""
        self.is_used = True
        self.save()

    def increment_attempts(self):
        """Incrémenter le nombre de tentatives"""
        self.attempts += 1
        self.save()


class Alert(BaseModel):
    """
    Modèle pour les alertes système
    """
    ALERT_TYPES = [
        ('stock_low', 'Stock bas'),
        ('stock_out', 'Rupture de stock'),
        ('invoice_overdue', 'Facture en retard'),
        ('order_pending', 'Commande en attente'),
        ('payment_failed', 'Paiement échoué'),
        ('system_error', 'Erreur système'),
        ('maintenance', 'Maintenance'),
        ('custom', 'Personnalisée'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('critical', 'Critique'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('read', 'Lue'),
        ('resolved', 'Résolue'),
        ('dismissed', 'Ignorée'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Titre",
        help_text="Titre de l'alerte"
    )
    message = models.TextField(
        verbose_name="Message",
        help_text="Message détaillé de l'alerte"
    )
    alert_type = models.CharField(
        max_length=50,
        choices=ALERT_TYPES,
        verbose_name="Type d'alerte",
        help_text="Type d'alerte"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium',
        verbose_name="Priorité",
        help_text="Niveau de priorité"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name="Statut",
        help_text="Statut de l'alerte"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Lue",
        help_text="Indique si l'alerte a été lue"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Utilisateur",
        help_text="Utilisateur concerné par l'alerte"
    )
    related_object_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Type d'objet lié",
        help_text="Type de l'objet lié (ex: Order, Invoice, Product)"
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID de l'objet lié",
        help_text="ID de l'objet lié"
    )
    action_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="URL d'action",
        help_text="URL vers l'objet concerné"
    )
    action_label = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Label d'action",
        help_text="Label du bouton d'action"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration",
        help_text="Date d'expiration de l'alerte"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées",
        help_text="Données supplémentaires au format JSON"
    )

    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['alert_type', 'priority']),
            models.Index(fields=['is_read', 'created_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_priority_display()}"

    def mark_as_read(self):
        """Marquer l'alerte comme lue"""
        self.is_read = True
        self.status = 'read'
        self.save()

    def mark_as_resolved(self):
        """Marquer l'alerte comme résolue"""
        self.status = 'resolved'
        self.save()

    def dismiss(self):
        """Ignorer l'alerte"""
        self.status = 'dismissed'
        self.save()

    def is_expired(self):
        """Vérifier si l'alerte est expirée"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class Notification(BaseModel):
    """
    Modèle pour les notifications utilisateur
    """
    NOTIFICATION_TYPES = [
        ('order_created', 'Commande créée'),
        ('order_updated', 'Commande mise à jour'),
        ('order_cancelled', 'Commande annulée'),
        ('invoice_created', 'Facture créée'),
        ('invoice_paid', 'Facture payée'),
        ('payment_received', 'Paiement reçu'),
        ('stock_alert', 'Alerte de stock'),
        ('user_action', 'Action utilisateur'),
        ('system_message', 'Message système'),
        ('reminder', 'Rappel'),
        ('custom', 'Personnalisée'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Faible'),
        ('medium', 'Moyenne'),
        ('high', 'Élevée'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('unread', 'Non lue'),
        ('read', 'Lue'),
        ('archived', 'Archivée'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name="Titre",
        help_text="Titre de la notification"
    )
    message = models.TextField(
        verbose_name="Message",
        help_text="Message de la notification"
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NOTIFICATION_TYPES,
        verbose_name="Type de notification",
        help_text="Type de notification"
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_LEVELS,
        default='medium',
        verbose_name="Priorité",
        help_text="Niveau de priorité"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='unread',
        verbose_name="Statut",
        help_text="Statut de la notification"
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="Lue",
        help_text="Indique si la notification a été lue"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Utilisateur",
        help_text="Utilisateur destinataire de la notification"
    )
    related_object_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Type d'objet lié",
        help_text="Type de l'objet lié (ex: Order, Invoice, Product)"
    )
    related_object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="ID de l'objet lié",
        help_text="ID de l'objet lié"
    )
    action_url = models.URLField(
        null=True,
        blank=True,
        verbose_name="URL d'action",
        help_text="URL vers l'objet concerné"
    )
    action_label = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="Label d'action",
        help_text="Label du bouton d'action"
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de lecture",
        help_text="Date à laquelle la notification a été lue"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'expiration",
        help_text="Date d'expiration de la notification"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Métadonnées",
        help_text="Données supplémentaires au format JSON"
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['is_read', 'created_at']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Marquer la notification comme lue"""
        self.is_read = True
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()

    def archive(self):
        """Archiver la notification"""
        self.status = 'archived'
        self.save()

    def is_expired(self):
        """Vérifier si la notification est expirée"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False