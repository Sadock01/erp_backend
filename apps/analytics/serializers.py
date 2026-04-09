from rest_framework import serializers


class KPISerializer(serializers.Serializer):
    """
    Serializer pour les KPIs
    """
    total_sales = serializers.DecimalField(max_digits=15, decimal_places=0)
    sales_growth = serializers.DecimalField(max_digits=5, decimal_places=1)
    avg_order_value = serializers.DecimalField(max_digits=15, decimal_places=0)
    aov_growth = serializers.DecimalField(max_digits=5, decimal_places=1)
    customer_lifetime_value = serializers.DecimalField(max_digits=15, decimal_places=0)
    clv_growth = serializers.DecimalField(max_digits=5, decimal_places=1)
    inventory_turnover = serializers.DecimalField(max_digits=5, decimal_places=1)
    turnover_growth = serializers.DecimalField(max_digits=5, decimal_places=1)


class ChartDatasetSerializer(serializers.Serializer):
    """
    Serializer pour les datasets de graphiques
    """
    label = serializers.CharField()
    data = serializers.ListField(child=serializers.DecimalField(max_digits=15, decimal_places=0))


class RevenueChartSerializer(serializers.Serializer):
    """
    Serializer pour le graphique des revenus
    """
    labels = serializers.ListField(child=serializers.CharField())
    datasets = ChartDatasetSerializer(many=True)


class SalesPerformanceChartSerializer(serializers.Serializer):
    """
    Serializer pour le graphique de performance des ventes
    """
    labels = serializers.ListField(child=serializers.CharField())
    datasets = ChartDatasetSerializer(many=True)


class TopCustomerSerializer(serializers.Serializer):
    """
    Serializer pour les top clients
    """
    rank = serializers.IntegerField()
    name = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=0)
    last_order = serializers.DateField()


class TopProductSerializer(serializers.Serializer):
    """
    Serializer pour les top produits
    """
    rank = serializers.IntegerField()
    name = serializers.CharField()
    category = serializers.CharField()
    sales = serializers.DecimalField(max_digits=15, decimal_places=0)
    units_sold = serializers.IntegerField()
    image = serializers.URLField()


class AnalyticsResponseSerializer(serializers.Serializer):
    """
    Serializer pour la réponse complète des analytics
    """
    kpis = KPISerializer()
    revenue_chart = RevenueChartSerializer()
    sales_performance_chart = SalesPerformanceChartSerializer()
    top_customers = TopCustomerSerializer(many=True)
    top_products = TopProductSerializer(many=True)


class ErrorResponseSerializer(serializers.Serializer):
    """
    Serializer pour les réponses d'erreur
    """
    error = serializers.DictField()
