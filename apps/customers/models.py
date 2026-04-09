from django.db import models
from django.core.validators import EmailValidator
from apps.common.models import BaseModel, Company


class Customer(BaseModel):
    """
    Modèle pour la gestion des clients
    Les clients n'ont pas besoin de s'inscrire, on crée juste leur profil
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire du client"
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Prénom",
        help_text="Prénom du client"
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name="Nom",
        help_text="Nom de famille du client"
    )
    email = models.EmailField(
        max_length=255,
        verbose_name="Email",
        help_text="Adresse email du client",
        validators=[EmailValidator()]
    )
    phone = models.CharField(
        max_length=20,
        verbose_name="Téléphone",
        help_text="Numéro de téléphone du client",
        blank=True,
        null=True
    )
    client_company = models.CharField(
        max_length=200,
        verbose_name="Entreprise du client",
        help_text="Nom de l'entreprise du client",
        blank=True,
        null=True
    )
    address = models.TextField(
        verbose_name="Adresse",
        help_text="Adresse complète du client",
        blank=True,
        null=True
    )
    city = models.CharField(
        max_length=100,
        verbose_name="Ville",
        help_text="Ville du client",
        blank=True,
        null=True
    )
    postal_code = models.CharField(
        max_length=10,
        verbose_name="Code postal",
        help_text="Code postal du client",
        blank=True,
        null=True
    )
    country = models.CharField(
        max_length=100,
        verbose_name="Pays",
        help_text="Pays du client",
        default="France"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
        help_text="Indique si le client est actif"
    )
    notes = models.TextField(
        verbose_name="Notes",
        help_text="Notes supplémentaires sur le client",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['last_name', 'first_name']
        unique_together = ['company', 'email']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['email']),
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        """Retourne le nom complet du client"""
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        """Retourne le nom court du client"""
        return f"{self.first_name} {self.last_name[0]}." if self.last_name else self.first_name
