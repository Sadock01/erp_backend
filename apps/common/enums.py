# Constantes et énumérations
from django.db import models


class ProductStatus(models.TextChoices):
    """Statuts des produits"""
    ACTIVE = 'active', 'Actif'
    INACTIVE = 'inactive', 'Inactif'
    DISCONTINUED = 'discontinued', 'Discontinué'
    OUT_OF_STOCK = 'out_of_stock', 'Rupture de stock'


class ProductType(models.TextChoices):
    """Types de produits"""
    SIMPLE = 'simple', 'Produit simple'
    VARIABLE = 'variable', 'Produit avec variants'
    BUNDLE = 'bundle', 'Pack/Lot'


class VariantType(models.TextChoices):
    """Types de variants"""
    SIZE = 'size', 'Taille'
    COLOR = 'color', 'Couleur'
    MATERIAL = 'material', 'Matière'
    STYLE = 'style', 'Style'
    OTHER = 'other', 'Autre'


class StockMovementType(models.TextChoices):
    """Types de mouvements de stock"""
    IN = 'in', 'Entrée'
    OUT = 'out', 'Sortie'
    ADJUSTMENT = 'adjustment', 'Ajustement'
    TRANSFER = 'transfer', 'Transfert'
    RETURN = 'return', 'Retour'


class OrderStatus(models.TextChoices):
    """Statuts des commandes"""
    DRAFT = 'draft', 'Brouillon'
    PENDING = 'pending', 'En attente'
    CONFIRMED = 'confirmed', 'Confirmée'
    PROCESSING = 'processing', 'En cours'
    SHIPPED = 'shipped', 'Expédiée'
    DELIVERED = 'delivered', 'Livrée'
    CANCELLED = 'cancelled', 'Annulée'


class InvoiceStatus(models.TextChoices):
    """Statuts des factures"""
    DRAFT = 'draft', 'Brouillon'
    SENT = 'sent', 'Envoyée'
    PAID = 'paid', 'Payée'
    OVERDUE = 'overdue', 'En retard'
    CANCELLED = 'cancelled', 'Annulée'
