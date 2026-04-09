from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.common.models import BaseModel, Company
from apps.common.enums import StockMovementType
from apps.inventory.models import Product, ProductVariant
from apps.customers.models import Customer


class StockMovement(BaseModel):
    """
    Modèle pour les mouvements de stock (entrées, sorties, ajustements)
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire du mouvement"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Produit",
        help_text="Produit concerné par le mouvement"
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        verbose_name="Variante",
        help_text="Variante du produit (optionnel)"
    )
    movement_type = models.CharField(
        max_length=20,
        choices=StockMovementType.choices,
        verbose_name="Type de mouvement",
        help_text="Type de mouvement de stock"
    )
    quantity = models.IntegerField(
        verbose_name="Quantité",
        help_text="Quantité du mouvement (positive pour entrée, négative pour sortie)"
    )
    unit_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Coût unitaire",
        help_text="Coût unitaire du produit lors du mouvement"
    )
    total_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Coût total",
        help_text="Coût total du mouvement"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Référence",
        help_text="Référence du mouvement (numéro de commande, facture, etc.)"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes supplémentaires sur le mouvement"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a effectué le mouvement"
    )
    is_approved = models.BooleanField(
        default=True,
        verbose_name="Approuvé",
        help_text="Indique si le mouvement est approuvé"
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='approved_movements',
        null=True,
        blank=True,
        verbose_name="Approuvé par",
        help_text="Utilisateur qui a approuvé le mouvement"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'approbation",
        help_text="Date et heure d'approbation"
    )

    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['product', 'movement_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reference']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} - {self.quantity}"

    def save(self, *args, **kwargs):
        # Calculer le coût total si coût unitaire fourni
        if self.unit_cost and self.quantity:
            self.total_cost = self.unit_cost * abs(self.quantity)
        super().save(*args, **kwargs)

    @property
    def is_entry(self):
        """Indique si c'est une entrée de stock"""
        return self.quantity > 0

    @property
    def is_exit(self):
        """Indique si c'est une sortie de stock"""
        return self.quantity < 0

    @property
    def absolute_quantity(self):
        """Quantité absolue"""
        return abs(self.quantity)


class StockAdjustment(BaseModel):
    """
    Modèle pour les ajustements manuels de stock
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire de l'ajustement"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Produit",
        help_text="Produit concerné par l'ajustement"
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        verbose_name="Variante",
        help_text="Variante du produit (optionnel)"
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=[
            ('inventory', 'Inventaire'),
            ('damage', 'Dégâts'),
            ('theft', 'Vol'),
            ('expired', 'Périmé'),
            ('other', 'Autre'),
        ],
        verbose_name="Type d'ajustement",
        help_text="Type d'ajustement de stock"
    )
    quantity_before = models.PositiveIntegerField(
        verbose_name="Quantité avant",
        help_text="Quantité en stock avant l'ajustement"
    )
    quantity_after = models.PositiveIntegerField(
        verbose_name="Quantité après",
        help_text="Quantité en stock après l'ajustement"
    )
    adjustment_quantity = models.IntegerField(
        verbose_name="Quantité d'ajustement",
        help_text="Quantité d'ajustement (positive ou négative)"
    )
    reason = models.TextField(
        verbose_name="Raison",
        help_text="Raison de l'ajustement"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a effectué l'ajustement"
    )
    is_approved = models.BooleanField(
        default=False,
        verbose_name="Approuvé",
        help_text="Indique si l'ajustement est approuvé"
    )
    approved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        related_name='approved_adjustments',
        null=True,
        blank=True,
        verbose_name="Approuvé par",
        help_text="Utilisateur qui a approuvé l'ajustement"
    )
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date d'approbation",
        help_text="Date et heure d'approbation"
    )

    class Meta:
        verbose_name = "Ajustement de stock"
        verbose_name_plural = "Ajustements de stock"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'adjustment_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_approved']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_adjustment_type_display()} - {self.adjustment_quantity}"

    def save(self, *args, **kwargs):
        # Calculer la quantité d'ajustement
        self.adjustment_quantity = self.quantity_after - self.quantity_before
        super().save(*args, **kwargs)


class StockAlert(BaseModel):
    """
    Modèle pour les alertes de stock bas
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire de l'alerte"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        verbose_name="Produit",
        help_text="Produit concerné par l'alerte"
    )
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        null=True,
        blank=True,
        verbose_name="Variante",
        help_text="Variante du produit (optionnel)"
    )
    alert_type = models.CharField(
        max_length=20,
        choices=[
            ('low_stock', 'Stock bas'),
            ('out_of_stock', 'Rupture de stock'),
            ('overstock', 'Surstock'),
        ],
        verbose_name="Type d'alerte",
        help_text="Type d'alerte de stock"
    )
    current_quantity = models.PositiveIntegerField(
        verbose_name="Quantité actuelle",
        help_text="Quantité actuelle en stock"
    )
    threshold_quantity = models.PositiveIntegerField(
        verbose_name="Quantité seuil",
        help_text="Quantité seuil pour déclencher l'alerte"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si l'alerte est active"
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name="Résolue",
        help_text="Indique si l'alerte a été résolue"
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de résolution",
        help_text="Date et heure de résolution"
    )
    resolved_by = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Résolu par",
        help_text="Utilisateur qui a résolu l'alerte"
    )

    class Meta:
        verbose_name = "Alerte de stock"
        verbose_name_plural = "Alertes de stock"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'alert_type']),
            models.Index(fields=['is_active', 'is_resolved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.get_alert_type_display()} - {self.current_quantity}"

    @property
    def is_low_stock(self):
        """Indique si c'est une alerte de stock bas"""
        return self.alert_type == 'low_stock'

    @property
    def is_out_of_stock(self):
        """Indique si c'est une alerte de rupture de stock"""
        return self.alert_type == 'out_of_stock'

    @property
    def is_overstock(self):
        """Indique si c'est une alerte de surstock"""
        return self.alert_type == 'overstock'


class StockReport(BaseModel):
    """
    Modèle pour les rapports de stock
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire du rapport"
    )
    report_type = models.CharField(
        max_length=20,
        choices=[
            ('inventory', 'Inventaire'),
            ('movements', 'Mouvements'),
            ('adjustments', 'Ajustements'),
            ('alerts', 'Alertes'),
            ('summary', 'Résumé'),
        ],
        verbose_name="Type de rapport",
        help_text="Type de rapport de stock"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Titre",
        help_text="Titre du rapport"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description du rapport"
    )
    date_from = models.DateField(
        verbose_name="Date de début",
        help_text="Date de début de la période du rapport"
    )
    date_to = models.DateField(
        verbose_name="Date de fin",
        help_text="Date de fin de la période du rapport"
    )
    filters = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Filtres",
        help_text="Filtres appliqués au rapport"
    )
    data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données",
        help_text="Données du rapport"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a généré le rapport"
    )
    is_generated = models.BooleanField(
        default=False,
        verbose_name="Généré",
        help_text="Indique si le rapport a été généré"
    )
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de génération",
        help_text="Date et heure de génération"
    )

    class Meta:
        verbose_name = "Rapport de stock"
        verbose_name_plural = "Rapports de stock"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['date_from', 'date_to']),
            models.Index(fields=['is_generated']),
        ]

    def __str__(self):
        return f"{self.title} - {self.get_report_type_display()}"

    @property
    def period_days(self):
        """Nombre de jours de la période"""
        return (self.date_to - self.date_from).days + 1