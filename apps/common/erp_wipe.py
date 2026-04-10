"""
Suppression ordonnée des données métier ERP.

Les FK en PROTECT (ex. Order → Customer, OrderItem → Product) empêchent
``Company.objects.all().delete()`` : il faut vider les tables dans le bon ordre.
"""

from __future__ import annotations

from django.db import transaction


def wipe_all_erp_tenant_data() -> None:
    """Supprime ventes, stock, catalogue, clients, caches, profils, rôles, entreprises."""
    from apps.analytics.models import AnalyticsCache
    from apps.common.models import Alert, Notification, UserProfile, Company
    from apps.customers.models import Customer
    from apps.inventory.models import Category, Product, ProductImage, ProductVariant
    from apps.permissions.models import UserRole
    from apps.sales.models import Invoice, Order, OrderItem, Payment, ProformaInvoice
    from apps.stock.models import StockAdjustment, StockAlert, StockMovement, StockReport

    with transaction.atomic():
        Payment.objects.all().delete()
        Invoice.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ProformaInvoice.objects.all().delete()

        StockMovement.objects.all().delete()
        StockAdjustment.objects.all().delete()
        StockAlert.objects.all().delete()
        StockReport.objects.all().delete()

        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()

        Customer.objects.all().delete()

        AnalyticsCache.objects.all().delete()
        Alert.objects.all().delete()
        Notification.objects.all().delete()

        UserProfile.objects.all().delete()
        UserRole.objects.all().delete()
        Company.objects.all().delete()
