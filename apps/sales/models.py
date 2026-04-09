from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.common.models import BaseModel, Company
from apps.common.enums import OrderStatus, InvoiceStatus
from apps.customers.models import Customer
from apps.inventory.models import Product, ProductVariant


class Order(BaseModel):
    """
    Modèle pour les commandes de vente
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire de la commande"
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name="Client",
        help_text="Client de la commande"
    )
    order_number = models.CharField(
        max_length=50,
        verbose_name="Numéro de commande",
        help_text="Numéro unique de la commande"
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="Statut",
        help_text="Statut de la commande"
    )
    order_date = models.DateTimeField(
        verbose_name="Date de commande",
        help_text="Date et heure de la commande"
    )
    delivery_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date de livraison",
        help_text="Date de livraison prévue"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Sous-total",
        help_text="Sous-total HT de la commande"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="Taux de TVA",
        help_text="Taux de TVA en pourcentage"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant TVA",
        help_text="Montant de la TVA"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total TTC",
        help_text="Total TTC de la commande"
    )
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="Taux de remise",
        help_text="Taux de remise en pourcentage"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant de remise",
        help_text="Montant de la remise"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur la commande"
    )
    internal_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes internes",
        help_text="Notes internes (non visibles par le client)"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a créé la commande"
    )

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-created_at']
        unique_together = ['company', 'order_number']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['order_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Commande {self.order_number} - {self.customer.full_name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        """Générer un numéro de commande unique"""
        from datetime import datetime
        now = datetime.now()
        prefix = f"CMD{now.strftime('%Y%m%d')}"
        last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
        if last_order:
            last_number = int(last_order.order_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}-{new_number:04d}"

    def calculate_totals(self):
        """Calculer les totaux de la commande"""
        items = self.items.all()
        self.subtotal = sum(item.total_price for item in items)
        
        if self.discount_rate > 0:
            self.discount_amount = self.subtotal * (self.discount_rate / 100)
            self.subtotal -= self.discount_amount
        
        self.tax_amount = self.subtotal * (self.tax_rate / 100)
        self.total_amount = self.subtotal + self.tax_amount
        self.save()

    @property
    def is_pending(self):
        return self.status == OrderStatus.PENDING

    @property
    def is_confirmed(self):
        return self.status == OrderStatus.CONFIRMED

    @property
    def is_shipped(self):
        return self.status == OrderStatus.SHIPPED

    @property
    def is_delivered(self):
        return self.status == OrderStatus.DELIVERED

    @property
    def is_cancelled(self):
        return self.status == OrderStatus.CANCELLED


class OrderItem(BaseModel):
    """
    Modèle pour les articles des commandes
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire de l'article"
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Commande",
        help_text="Commande parente"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="Produit",
        help_text="Produit commandé"
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name="Variante",
        help_text="Variante du produit (optionnel)"
    )
    quantity = models.PositiveIntegerField(
        verbose_name="Quantité",
        help_text="Quantité commandée"
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix unitaire",
        help_text="Prix unitaire HT"
    )
    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="Taux de remise",
        help_text="Taux de remise en pourcentage"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant de remise",
        help_text="Montant de la remise"
    )
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Prix total",
        help_text="Prix total HT de l'article"
    )

    class Meta:
        verbose_name = "Article de commande"
        verbose_name_plural = "Articles de commande"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['order', 'product']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity} - {self.order.order_number}"

    def save(self, *args, **kwargs):
        self.calculate_total()
        super().save(*args, **kwargs)

    def calculate_total(self):
        """Calculer le prix total de l'article"""
        base_price = self.unit_price * self.quantity
        
        if self.discount_rate > 0:
            self.discount_amount = base_price * (self.discount_rate / 100)
            self.total_price = base_price - self.discount_amount
        else:
            self.total_price = base_price

    @property
    def product_name(self):
        """Nom du produit avec variante"""
        if self.variant:
            return f"{self.product.name} - {self.variant.name}"
        return self.product.name

    @property
    def final_unit_price(self):
        """Prix unitaire final après remise"""
        if self.discount_rate > 0:
            return self.unit_price * (1 - self.discount_rate / 100)
        return self.unit_price


class Invoice(BaseModel):
    """
    Modèle pour les factures
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        verbose_name="Entreprise",
        help_text="Entreprise propriétaire de la facture"
    )
    order = models.OneToOneField(
        Order,
        on_delete=models.PROTECT,
        related_name='invoice',
        verbose_name="Commande",
        help_text="Commande facturée"
    )
    invoice_number = models.CharField(
        max_length=50,
        verbose_name="Numéro de facture",
        help_text="Numéro unique de la facture"
    )
    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT,
        verbose_name="Statut",
        help_text="Statut de la facture"
    )
    invoice_date = models.DateTimeField(
        verbose_name="Date de facture",
        help_text="Date de la facture"
    )
    due_date = models.DateTimeField(
        verbose_name="Date d'échéance",
        help_text="Date d'échéance de paiement"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Sous-total",
        help_text="Sous-total HT de la facture"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Taux de TVA",
        help_text="Taux de TVA en pourcentage"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant TVA",
        help_text="Montant de la TVA"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Total TTC",
        help_text="Total TTC de la facture"
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant payé",
        help_text="Montant déjà payé"
    )
    remaining_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Montant restant",
        help_text="Montant restant à payer"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur la facture"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a créé la facture"
    )

    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-created_at']
        unique_together = ['company', 'invoice_number']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['invoice_number']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_date']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Facture {self.invoice_number} - {self.order.customer.full_name}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()
        super().save(*args, **kwargs)

    def generate_invoice_number(self):
        """Générer un numéro de facture unique"""
        from datetime import datetime
        now = datetime.now()
        prefix = f"FAC{now.strftime('%Y%m%d')}"
        last_invoice = Invoice.objects.filter(invoice_number__startswith=prefix).order_by('-invoice_number').first()
        if last_invoice:
            last_number = int(last_invoice.invoice_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}-{new_number:04d}"

    def calculate_totals(self):
        """Calculer les totaux de la facture"""
        self.subtotal = self.order.subtotal
        self.tax_rate = self.order.tax_rate
        self.tax_amount = self.order.tax_amount
        self.total_amount = self.order.total_amount
        self.remaining_amount = self.total_amount - self.paid_amount
        self.save()

    @property
    def is_draft(self):
        return self.status == InvoiceStatus.DRAFT

    @property
    def is_sent(self):
        return self.status == InvoiceStatus.SENT

    @property
    def is_paid(self):
        return self.status == InvoiceStatus.PAID

    @property
    def is_overdue(self):
        from django.utils import timezone
        return self.status != InvoiceStatus.PAID and timezone.now() > self.due_date

    @property
    def payment_percentage(self):
        """Pourcentage de paiement"""
        if self.total_amount > 0:
            return (self.paid_amount / self.total_amount) * 100
        return 0


class ProformaInvoice(BaseModel):
    """
    Modèle pour les devis/factures proforma
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        verbose_name="Client",
        help_text="Client du devis"
    )
    proforma_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro de devis",
        help_text="Numéro unique du devis"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Brouillon'),
            ('sent', 'Envoyé'),
            ('accepted', 'Accepté'),
            ('rejected', 'Rejeté'),
            ('expired', 'Expiré'),
        ],
        default='draft',
        verbose_name="Statut",
        help_text="Statut du devis"
    )
    proforma_date = models.DateTimeField(
        verbose_name="Date du devis",
        help_text="Date du devis"
    )
    valid_until = models.DateTimeField(
        verbose_name="Valide jusqu'au",
        help_text="Date de validité du devis"
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Sous-total",
        help_text="Sous-total HT du devis"
    )
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('20.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        verbose_name="Taux de TVA",
        help_text="Taux de TVA en pourcentage"
    )
    tax_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Montant TVA",
        help_text="Montant de la TVA"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total TTC",
        help_text="Total TTC du devis"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur le devis"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a créé le devis"
    )

    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['proforma_number']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['proforma_date']),
            models.Index(fields=['valid_until']),
        ]

    def __str__(self):
        return f"Devis {self.proforma_number} - {self.customer.full_name}"

    def save(self, *args, **kwargs):
        if not self.proforma_number:
            self.proforma_number = self.generate_proforma_number()
        super().save(*args, **kwargs)

    def generate_proforma_number(self):
        """Générer un numéro de devis unique"""
        from datetime import datetime
        now = datetime.now()
        prefix = f"DEV{now.strftime('%Y%m%d')}"
        last_proforma = ProformaInvoice.objects.filter(proforma_number__startswith=prefix).order_by('-proforma_number').first()
        if last_proforma:
            last_number = int(last_proforma.proforma_number.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1
        return f"{prefix}-{new_number:04d}"

    @property
    def is_draft(self):
        return self.status == 'draft'

    @property
    def is_sent(self):
        return self.status == 'sent'

    @property
    def is_accepted(self):
        return self.status == 'accepted'

    @property
    def is_rejected(self):
        return self.status == 'rejected'

    @property
    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.valid_until


class Payment(BaseModel):
    """
    Modèle pour les paiements
    """
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Facture",
        help_text="Facture payée"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Espèces'),
            ('check', 'Chèque'),
            ('bank_transfer', 'Virement bancaire'),
            ('credit_card', 'Carte de crédit'),
            ('paypal', 'PayPal'),
            ('other', 'Autre'),
        ],
        verbose_name="Méthode de paiement",
        help_text="Méthode de paiement utilisée"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant",
        help_text="Montant du paiement"
    )
    payment_date = models.DateTimeField(
        verbose_name="Date de paiement",
        help_text="Date du paiement"
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Référence",
        help_text="Référence du paiement (numéro de chèque, virement, etc.)"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Notes",
        help_text="Notes sur le paiement"
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name="Utilisateur",
        help_text="Utilisateur qui a enregistré le paiement"
    )

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['invoice', 'payment_date']),
            models.Index(fields=['payment_method']),
            models.Index(fields=['payment_date']),
        ]

    def __str__(self):
        return f"Paiement {self.amount}€ - {self.invoice.invoice_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Mettre à jour le montant payé de la facture
        self.invoice.calculate_totals()