from django.db import models
from apps.common.models import BaseModel


class AnalyticsCache(BaseModel):
    """
    Cache pour les données analytics
    """
    cache_key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Clé de cache",
        help_text="Clé unique pour identifier le cache"
    )
    data = models.JSONField(
        verbose_name="Données",
        help_text="Données mises en cache"
    )
    expires_at = models.DateTimeField(
        verbose_name="Expire à",
        help_text="Date d'expiration du cache"
    )
    cache_type = models.CharField(
        max_length=50,
        choices=[
            ('kpis', 'KPIs'),
            ('revenue_chart', 'Graphique des revenus'),
            ('sales_performance', 'Performance des ventes'),
            ('top_customers', 'Top clients'),
            ('top_products', 'Top produits'),
            ('full_data', 'Données complètes'),
        ],
        verbose_name="Type de cache",
        help_text="Type de données mises en cache"
    )

    class Meta:
        verbose_name = "Cache Analytics"
        verbose_name_plural = "Caches Analytics"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['cache_key']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['cache_type']),
        ]

    def __str__(self):
        return f"Cache {self.cache_type} - {self.cache_key}"

    def is_expired(self):
        """Vérifier si le cache est expiré"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
