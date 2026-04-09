from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from apps.common.models import BaseModel, Company
from apps.common.enums import ProductStatus, ProductType, VariantType


class Category(BaseModel):
    """
    Catégorie de produits
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,verbose_name="Entreprise",
        help_text="Entreprise propriétaire de la catégorie"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nom",
        help_text="Nom de la catégorie"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description de la catégorie"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,verbose_name="Catégorie parente",
        help_text="Catégorie parente pour créer une hiérarchie"
    )
    image = models.ImageField(
        upload_to='categories/',
        blank=True,
        null=True,
        verbose_name="Image",
        help_text="Image de la catégorie"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si la catégorie est active"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre de tri",
        help_text="Ordre d'affichage de la catégorie"
    )

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['sort_order', 'name']
        unique_together = ['company', 'name']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['is_active']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name

    @property
    def full_name(self):
        """Retourne le nom complet avec la hiérarchie"""
        if self.parent:
            return f"{self.parent.full_name} > {self.name}"
        return self.name


class Product(BaseModel):
    """
    Produit principal
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,verbose_name="Entreprise",
        help_text="Entreprise propriétaire du produit"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Nom",
        help_text="Nom du produit"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Description",
        help_text="Description détaillée du produit"
    )
    short_description = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Description courte",
        help_text="Description courte du produit"
    )
    sku = models.CharField(
        max_length=100,
        verbose_name="SKU",
        help_text="Code produit unique (SKU)"
    )
    barcode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Code-barres",
        help_text="Code-barres du produit"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        verbose_name="Catégorie",
        help_text="Catégorie du produit"
    )
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        default=ProductType.SIMPLE,
        verbose_name="Type de produit",
        help_text="Type de produit"
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.ACTIVE,
        verbose_name="Statut",
        help_text="Statut du produit"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Prix",
        help_text="Prix de base du produit"
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Prix de revient",
        help_text="Prix de revient du produit"
    )
    weight = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name="Poids (kg)",
        help_text="Poids du produit en kilogrammes"
    )
    dimensions = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Dimensions",
        help_text="Dimensions du produit (L x l x H)"
    )
    is_digital = models.BooleanField(
        default=False,
        verbose_name="Produit numérique",
        help_text="Indique si c'est un produit numérique"
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name="Produit vedette",
        help_text="Indique si c'est un produit mis en avant"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Tags",
        help_text="Tags séparés par des virgules"
    )
    meta_title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Meta titre",
        help_text="Titre SEO"
    )
    meta_description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Meta description",
        help_text="Description SEO"
    )

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['name']
        unique_together = ['company', 'sku']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['product_type']),
            models.Index(fields=['is_featured']),
        ]

    def __str__(self):
        return f"{self.name} ({self.sku})"

    @property
    def tag_list(self):
        """Retourne la liste des tags"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

    def get_stock_quantity(self):
        """Retourne la quantité en stock totale"""
        return sum(variant.stock_quantity for variant in self.variants.all())


class ProductVariant(BaseModel):
    """
    Variante d'un produit (taille, couleur, etc.)
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,verbose_name="Entreprise",
        help_text="Entreprise propriétaire de la variante"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name="Produit",
        help_text="Produit parent"
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nom de la variante",
        help_text="Nom de la variante (ex: Rouge, Taille L)"
    )
    sku = models.CharField(
        max_length=100,
        verbose_name="SKU",
        help_text="Code unique de la variante"
    )
    variant_type = models.CharField(
        max_length=20,
        choices=VariantType.choices,
        default=VariantType.OTHER,
        verbose_name="Type de variante",
        help_text="Type de variante"
    )
    value = models.CharField(
        max_length=100,
        verbose_name="Valeur",
        help_text="Valeur de la variante (ex: Rouge, L, Cuir)"
    )
    price_modifier = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Modificateur de prix",
        help_text="Modification du prix par rapport au produit de base"
    )
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name="Quantité en stock",
        help_text="Quantité disponible en stock"
    )
    min_stock_level = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock minimum",
        help_text="Niveau de stock minimum avant alerte"
    )
    max_stock_level = models.PositiveIntegerField(
        default=1000,
        verbose_name="Stock maximum",
        help_text="Niveau de stock maximum"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Indique si la variante est active"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre de tri",
        help_text="Ordre d'affichage de la variante"
    )

    class Meta:
        verbose_name = "Variante de produit"
        verbose_name_plural = "Variantes de produit"
        ordering = ['product', 'sort_order', 'name']
        unique_together = ['company', 'sku']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['product']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active']),
            models.Index(fields=['stock_quantity']),
        ]

    def __str__(self):
        return f"{self.product.name} - {self.name}"

    @property
    def final_price(self):
        """Retourne le prix final de la variante"""
        return self.product.price + self.price_modifier

    @property
    def is_low_stock(self):
        """Indique si le stock est faible"""
        return self.stock_quantity <= self.min_stock_level

    @property
    def is_out_of_stock(self):
        """Indique si le produit est en rupture de stock"""
        return self.stock_quantity <= 0


class ProductImage(BaseModel):
    """
    Image d'un produit ou d'un variant
    """
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,verbose_name="Entreprise",
        help_text="Entreprise propriétaire de l'image"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Produit",
        help_text="Produit associé",
        null=True,
        blank=True
    )
    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Variant",
        help_text="Variant associé",
        null=True,
        blank=True
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Image",
        help_text="Image du produit"
    )
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Texte alternatif",
        help_text="Texte alternatif pour l'accessibilité"
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Image principale",
        help_text="Indique si c'est l'image principale"
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre de tri",
        help_text="Ordre d'affichage de l'image"
    )

    class Meta:
        verbose_name = "Image de produit"
        verbose_name_plural = "Images de produit"
        ordering = ['product', 'variant', 'sort_order']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['product']),
            models.Index(fields=['variant']),
            models.Index(fields=['is_primary']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(product__isnull=False, variant__isnull=True) |
                    models.Q(product__isnull=True, variant__isnull=False)
                ),
                name='product_or_variant_required'
            )
        ]

    def clean(self):
        """Validation : une image doit être liée soit à un produit soit à un variant"""
        from django.core.exceptions import ValidationError
        if not self.product and not self.variant:
            raise ValidationError("Une image doit être liée soit à un produit soit à un variant")
        if self.product and self.variant:
            raise ValidationError("Une image ne peut pas être liée à la fois à un produit et à un variant")

    def __str__(self):
        return f"{self.product.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule image principale par produit
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)
