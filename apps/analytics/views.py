from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, F, Max
from django.db import models
from datetime import datetime, timedelta
import hashlib
import json

from .models import AnalyticsCache
from .serializers import (
    AnalyticsResponseSerializer,
    KPISerializer,
    RevenueChartSerializer,
    SalesPerformanceChartSerializer,
    TopCustomerSerializer,
    TopProductSerializer,
    ErrorResponseSerializer
)
from apps.permissions.decorators import user_has_permission


def get_user_company_or_all(user):
    """
    Retourne la company de l'utilisateur ou None si Super Admin.
    Si l'utilisateur est Super Admin (permission companies_view_all), retourne None pour voir toutes les données.
    """
    # Si l'utilisateur est un Super Admin avec la permission 'companies_view_all', il voit tout
    if user_has_permission(user, 'companies_view_all'):
        return None
    
    # Sinon, retourner la company de l'utilisateur
    try:
        return user.userprofile.company
    except AttributeError:
        # L'utilisateur n'a pas de profil ou d'entreprise associée
        return None


def get_cache_key(params):
    """Générer une clé de cache basée sur les paramètres"""
    params_str = json.dumps(params, sort_keys=True)
    return hashlib.md5(params_str.encode()).hexdigest()


def get_cached_data(cache_key, cache_type):
    """Récupérer les données du cache"""
    try:
        cache_obj = AnalyticsCache.objects.get(
            cache_key=cache_key,
            cache_type=cache_type
        )
        if not cache_obj.is_expired():
            return cache_obj.data
        else:
            cache_obj.delete()
    except AnalyticsCache.DoesNotExist:
        pass
    return None


def set_cached_data(cache_key, cache_type, data, cache_duration_minutes=5):
    """Mettre en cache les données"""
    expires_at = timezone.now() + timedelta(minutes=cache_duration_minutes)
    AnalyticsCache.objects.update_or_create(
        cache_key=cache_key,
        cache_type=cache_type,
        defaults={
            'data': data,
            'expires_at': expires_at
        }
    )


def get_date_range(period, custom_start_date=None, custom_end_date=None):
    """Calculer la plage de dates selon la période"""
    now = timezone.now().date()
    
    if period == '7d':
        start_date = now - timedelta(days=7)
        end_date = now
    elif period == '30d':
        start_date = now - timedelta(days=30)
        end_date = now
    elif period == '90d':
        start_date = now - timedelta(days=90)
        end_date = now
    elif period == '1y':
        start_date = now - timedelta(days=365)
        end_date = now
    elif period == 'custom':
        if not custom_start_date or not custom_end_date:
            raise ValueError("custom_start_date et custom_end_date sont requis pour la période custom")
        start_date = datetime.strptime(custom_start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(custom_end_date, '%Y-%m-%d').date()
    else:
        raise ValueError("Période invalide. Utilisez 7d, 30d, 90d, 1y ou custom")
    
    return start_date, end_date


def _generate_revenue_chart(start_date, end_date, order_filter):
    """Générer le graphique des revenus basé sur de vraies données"""
    from django.db.models import Sum
    from apps.sales.models import Order
    
    period_days = (end_date - start_date).days
    
    if period_days <= 7:
        # Données quotidiennes
        labels = []
        data = []
        for i in range(period_days):
            current_date = start_date + timedelta(days=i)
            labels.append(current_date.strftime('%a'))
            
            daily_revenue = Order.objects.filter(
                created_at__date=current_date,
                status__in=['confirmed', 'shipped', 'delivered'],
                **order_filter
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            data.append(float(daily_revenue))
    elif period_days <= 30:
        # Données hebdomadaires
        labels = []
        data = []
        weeks = (period_days + 6) // 7
        for i in range(weeks):
            week_start = start_date + timedelta(days=i*7)
            week_end = min(week_start + timedelta(days=6), end_date)
            labels.append(f"Sem {i+1}")
            
            weekly_revenue = Order.objects.filter(
                created_at__date__gte=week_start,
                created_at__date__lte=week_end,
                status__in=['confirmed', 'shipped', 'delivered'],
                **order_filter
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            data.append(float(weekly_revenue))
    else:
        # Données mensuelles
        labels = []
        data = []
        months = (period_days + 29) // 30
        for i in range(months):
            month_start = start_date + timedelta(days=i*30)
            month_end = min(month_start + timedelta(days=29), end_date)
            labels.append(f"Mois {i+1}")
            
            monthly_revenue = Order.objects.filter(
                created_at__date__gte=month_start,
                created_at__date__lte=month_end,
                status__in=['confirmed', 'shipped', 'delivered'],
                **order_filter
            ).aggregate(total=Sum('total_amount'))['total'] or 0
            data.append(float(monthly_revenue))
    
    return {
        'labels': labels,
        'datasets': [{
            'label': 'Revenus (FCFA)',
            'data': data
        }]
    }


def _generate_sales_performance_chart(start_date, end_date, order_filter, product_filter):
    """Générer le graphique de performance des ventes par catégorie"""
    from django.db.models import Sum
    from apps.sales.models import OrderItem
    from apps.inventory.models import Category
    
    # Récupérer les catégories avec des ventes
    categories = Category.objects.filter(**product_filter).annotate(
        total_sales=Sum('product__orderitem__quantity', 
                       filter=Q(product__orderitem__order__created_at__date__gte=start_date,
                               product__orderitem__order__created_at__date__lte=end_date,
                               product__orderitem__order__status__in=['confirmed', 'shipped', 'delivered'],
                               **order_filter)
        )
    ).filter(total_sales__gt=0).order_by('-total_sales')[:6]
    
    labels = [cat.name for cat in categories]
    data = [float(cat.total_sales or 0) for cat in categories]
    
    return {
        'labels': labels,
        'datasets': [{
            'label': 'Chiffre d\'affaires (FCFA)',
            'data': data
        }]
    }


def _generate_top_customers(start_date, end_date, customer_filter, order_filter):
    """Générer la liste des top clients"""
    from django.db.models import Sum, Count
    from apps.customers.models import Customer
    from apps.sales.models import Order
    
    top_customers = Customer.objects.filter(**customer_filter).annotate(
        total_spent=Sum('order__total_amount',
                       filter=Q(order__created_at__date__gte=start_date,
                               order__created_at__date__lte=end_date,
                               order__status__in=['confirmed', 'shipped', 'delivered'],
                               **order_filter)
        ),
        total_orders=Count('order',
                          filter=Q(order__created_at__date__gte=start_date,
                                  order__created_at__date__lte=end_date,
                                  order__status__in=['confirmed', 'shipped', 'delivered'],
                                  **order_filter)
        ),
        last_order_date=Max('order__created_at',
                           filter=Q(order__created_at__date__gte=start_date,
                                   order__created_at__date__lte=end_date,
                                   order__status__in=['confirmed', 'shipped', 'delivered'],
                                   **order_filter)
        )
    ).filter(total_spent__gt=0).order_by('-total_spent')[:5]
    
    result = []
    for i, customer in enumerate(top_customers, 1):
        result.append({
            'rank': i,
            'name': f"{customer.first_name} {customer.last_name}".strip() or customer.email,
            'total_orders': customer.total_orders or 0,
            'total_spent': float(customer.total_spent or 0),
            'last_order': customer.last_order_date.strftime('%Y-%m-%d') if customer.last_order_date else None
        })
    
    return result


def _generate_top_products(start_date, end_date, order_filter, product_filter):
    """Générer la liste des top produits"""
    from django.db.models import Sum
    from apps.sales.models import OrderItem
    from apps.inventory.models import Product
    
    top_products = Product.objects.filter(**product_filter).annotate(
        total_sales=Sum('orderitem__quantity',
                       filter=Q(orderitem__order__created_at__date__gte=start_date,
                               orderitem__order__created_at__date__lte=end_date,
                               orderitem__order__status__in=['confirmed', 'shipped', 'delivered'],
                               **order_filter)
        ),
        total_revenue=Sum(F('orderitem__quantity') * F('orderitem__unit_price'),
                         filter=Q(orderitem__order__created_at__date__gte=start_date,
                                 orderitem__order__created_at__date__lte=end_date,
                                 orderitem__order__status__in=['confirmed', 'shipped', 'delivered'],
                                 **order_filter),
                         output_field=models.DecimalField()
        )
    ).filter(total_sales__gt=0).order_by('-total_revenue')[:5]
    
    result = []
    for i, product in enumerate(top_products, 1):
        result.append({
            'rank': i,
            'name': product.name,
            'category': product.category.name if product.category else 'Sans catégorie',
            'sales': float(product.total_revenue or 0),
            'units_sold': int(product.total_sales or 0),
            'image': product.images.first().image.url if product.images.exists() else None
        })
    
    return result


def generate_real_data(start_date, end_date, user_company=None, customer_segment='all', product_category='all', revenue_min=0, revenue_max=10000000):
    """Générer des données réelles basées sur la base de données"""
    from django.db.models import Sum, Count, Avg, F
    from apps.sales.models import Order, OrderItem, Invoice
    from apps.customers.models import Customer
    from apps.inventory.models import Product, ProductVariant, Category
    
    # Filtrage par company si nécessaire
    order_filter = {}
    customer_filter = {}
    product_filter = {}
    
    if user_company:
        order_filter['company'] = user_company
        customer_filter['company'] = user_company
        product_filter['company'] = user_company
    
    # Convertir les dates en datetime pour les requêtes
    start_datetime = timezone.make_aware(datetime.combine(start_date, datetime.min.time()))
    end_datetime = timezone.make_aware(datetime.combine(end_date, datetime.max.time()))
    
    # KPIs - Revenus
    total_sales = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status__in=['confirmed', 'shipped', 'delivered'],
        **order_filter
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculer la croissance des ventes (comparaison avec la période précédente)
    period_days = (end_date - start_date).days
    previous_start = start_date - timedelta(days=period_days)
    previous_sales = Order.objects.filter(
        created_at__date__gte=previous_start,
        created_at__date__lt=start_date,
        status__in=['confirmed', 'shipped', 'delivered'],
        **order_filter
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    sales_growth = 0.0
    if previous_sales > 0:
        sales_growth = ((total_sales - previous_sales) / previous_sales) * 100
    
    # KPIs - Valeur moyenne des commandes
    avg_order_value = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        status__in=['confirmed', 'shipped', 'delivered'],
        **order_filter
    ).aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    # Calculer la croissance de la valeur moyenne des commandes
    previous_avg = Order.objects.filter(
        created_at__date__gte=previous_start,
        created_at__date__lt=start_date,
        status__in=['confirmed', 'shipped', 'delivered'],
        **order_filter
    ).aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    aov_growth = 0.0
    if previous_avg > 0:
        aov_growth = ((avg_order_value - previous_avg) / previous_avg) * 100
    
    # KPIs - Valeur vie client (CLV)
    customer_lifetime_value = Customer.objects.filter(**customer_filter).aggregate(
        clv=Avg('order__total_amount')
    )['clv'] or 0
    
    # Calculer la croissance du CLV
    previous_clv = Customer.objects.filter(**customer_filter).aggregate(
        clv=Avg('order__total_amount')
    )['clv'] or 0
    
    clv_growth = 0.0
    if previous_clv > 0:
        clv_growth = ((customer_lifetime_value - previous_clv) / previous_clv) * 100
    
    # KPIs - Rotation des stocks (simplifié)
    inventory_turnover = 0.0
    turnover_growth = 0.0
    
    # Graphique des revenus par période
    revenue_chart = _generate_revenue_chart(start_date, end_date, order_filter)
    
    # Graphique de performance des ventes par catégorie
    sales_performance_chart = _generate_sales_performance_chart(start_date, end_date, order_filter, product_filter)
    
    # Top clients
    top_customers = _generate_top_customers(start_date, end_date, customer_filter, order_filter)
    
    # Top produits
    top_products = _generate_top_products(start_date, end_date, order_filter, product_filter)
    
    return {
        'kpis': {
            'total_sales': float(total_sales),
            'sales_growth': round(float(sales_growth), 2),
            'avg_order_value': float(avg_order_value),
            'aov_growth': round(float(aov_growth), 2),
            'customer_lifetime_value': float(customer_lifetime_value),
            'clv_growth': round(float(clv_growth), 2),
            'inventory_turnover': float(inventory_turnover),
            'turnover_growth': float(turnover_growth)
        },
        'revenue_chart': revenue_chart,
        'sales_performance_chart': sales_performance_chart,
        'top_customers': top_customers,
        'top_products': top_products
    }


def generate_sample_data(start_date, end_date, customer_segment='all', product_category='all', revenue_min=0, revenue_max=10000000):
    """Générer des données d'exemple pour les analytics basées sur les paramètres"""
    
    # Convertir les paramètres de revenus en entiers
    try:
        revenue_min = int(revenue_min) if revenue_min else 0
        revenue_max = int(revenue_max) if revenue_max else 10000000
    except (ValueError, TypeError):
        revenue_min = 0
        revenue_max = 10000000
    
    # Calculer la durée en jours pour ajuster les données
    duration_days = (end_date - start_date).days
    
    # Ajuster les KPIs selon la période
    base_sales = 7800000
    if duration_days <= 7:
        # 7 jours : données plus faibles
        total_sales = int(base_sales * 0.2)
        sales_growth = 5.2
        avg_order_value = 95000
        aov_growth = 3.1
        customer_lifetime_value = 320000
        clv_growth = 8.5
        inventory_turnover = 2.8
        turnover_growth = -2.1
    elif duration_days <= 30:
        # 30 jours : données de base
        total_sales = base_sales
        sales_growth = 12.5
        avg_order_value = 125000
        aov_growth = 8.3
        customer_lifetime_value = 450000
        clv_growth = 15.2
        inventory_turnover = 4.2
        turnover_growth = -5.2
    elif duration_days <= 90:
        # 90 jours : données plus élevées
        total_sales = int(base_sales * 2.5)
        sales_growth = 18.7
        avg_order_value = 145000
        aov_growth = 12.1
        customer_lifetime_value = 520000
        clv_growth = 22.3
        inventory_turnover = 5.8
        turnover_growth = 2.4
    else:
        # 1 an : données maximales
        total_sales = int(base_sales * 8.5)
        sales_growth = 25.3
        avg_order_value = 165000
        aov_growth = 18.7
        customer_lifetime_value = 680000
        clv_growth = 35.1
        inventory_turnover = 7.2
        turnover_growth = 8.9
    
    # Ajuster selon le segment client
    if customer_segment == 'vip':
        total_sales = int(total_sales * 1.5)
        avg_order_value = int(avg_order_value * 1.3)
    elif customer_segment == 'new':
        total_sales = int(total_sales * 0.6)
        avg_order_value = int(avg_order_value * 0.8)
    elif customer_segment == 'inactive':
        total_sales = int(total_sales * 0.3)
        avg_order_value = int(avg_order_value * 0.7)
    
    # Ajuster selon la catégorie de produit
    if product_category == 'electronics':
        total_sales = int(total_sales * 1.4)
        avg_order_value = int(avg_order_value * 1.2)
    elif product_category == 'clothing':
        total_sales = int(total_sales * 0.8)
        avg_order_value = int(avg_order_value * 0.9)
    elif product_category == 'sports':
        total_sales = int(total_sales * 0.7)
        avg_order_value = int(avg_order_value * 0.85)
    
    # Appliquer les filtres de revenus
    if total_sales < revenue_min:
        total_sales = revenue_min
    if total_sales > revenue_max:
        total_sales = revenue_max
    
    # KPIs
    kpis = {
        'total_sales': total_sales,
        'sales_growth': sales_growth,
        'avg_order_value': avg_order_value,
        'aov_growth': aov_growth,
        'customer_lifetime_value': customer_lifetime_value,
        'clv_growth': clv_growth,
        'inventory_turnover': inventory_turnover,
        'turnover_growth': turnover_growth
    }
    
    # Graphique des revenus (ajusté selon la période)
    if duration_days <= 7:
        # 7 jours : données quotidiennes
        revenue_chart = {
            'labels': ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
            'datasets': [{
                'label': 'Revenus (FCFA)',
                'data': [int(total_sales * 0.12), int(total_sales * 0.15), int(total_sales * 0.11), 
                        int(total_sales * 0.18), int(total_sales * 0.20), int(total_sales * 0.14), int(total_sales * 0.10)]
            }]
        }
    elif duration_days <= 30:
        # 30 jours : données hebdomadaires
        revenue_chart = {
            'labels': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
            'datasets': [{
                'label': 'Revenus (FCFA)',
                'data': [int(total_sales * 0.22), int(total_sales * 0.28), int(total_sales * 0.25), int(total_sales * 0.25)]
            }]
        }
    elif duration_days <= 90:
        # 90 jours : données mensuelles
        revenue_chart = {
            'labels': ['Mois 1', 'Mois 2', 'Mois 3'],
            'datasets': [{
                'label': 'Revenus (FCFA)',
                'data': [int(total_sales * 0.30), int(total_sales * 0.35), int(total_sales * 0.35)]
            }]
        }
    else:
        # 1 an : données trimestrielles
        revenue_chart = {
            'labels': ['Q1', 'Q2', 'Q3', 'Q4'],
            'datasets': [{
                'label': 'Revenus (FCFA)',
                'data': [int(total_sales * 0.20), int(total_sales * 0.25), int(total_sales * 0.30), int(total_sales * 0.25)]
            }]
        }
    
    # Graphique de performance des ventes (ajusté selon la catégorie)
    if product_category == 'electronics':
        sales_performance_chart = {
            'labels': ['Électronique', 'Accessoires', 'Composants', 'Logiciels', 'Services Tech'],
            'datasets': [{
                'label': 'Chiffre d\'affaires (FCFA)',
                'data': [int(total_sales * 0.6), int(total_sales * 0.2), int(total_sales * 0.1), 
                        int(total_sales * 0.05), int(total_sales * 0.05)]
            }]
        }
    elif product_category == 'clothing':
        sales_performance_chart = {
            'labels': ['Vêtements', 'Chaussures', 'Accessoires', 'Maroquinerie', 'Bijoux'],
            'datasets': [{
                'label': 'Chiffre d\'affaires (FCFA)',
                'data': [int(total_sales * 0.5), int(total_sales * 0.25), int(total_sales * 0.15), 
                        int(total_sales * 0.05), int(total_sales * 0.05)]
            }]
        }
    elif product_category == 'sports':
        sales_performance_chart = {
            'labels': ['Sport & Loisirs', 'Équipements', 'Nutrition', 'Vêtements Sport', 'Accessoires'],
            'datasets': [{
                'label': 'Chiffre d\'affaires (FCFA)',
                'data': [int(total_sales * 0.4), int(total_sales * 0.3), int(total_sales * 0.15), 
                        int(total_sales * 0.1), int(total_sales * 0.05)]
            }]
        }
    else:
        # Toutes catégories
        sales_performance_chart = {
            'labels': ['Électronique', 'Vêtements', 'Maison & Jardin', 'Sport & Loisirs', 'Livres & Médias', 'Beauté & Santé'],
            'datasets': [{
                'label': 'Chiffre d\'affaires (FCFA)',
                'data': [int(total_sales * 0.32), int(total_sales * 0.23), int(total_sales * 0.15), 
                        int(total_sales * 0.12), int(total_sales * 0.08), int(total_sales * 0.10)]
            }]
        }
    
    # Top clients (ajusté selon le segment)
    if customer_segment == 'vip':
        top_customers = [
            {
                'rank': 1,
                'name': 'SARL Tech Solutions VIP',
                'total_orders': 85,
                'total_spent': int(total_sales * 0.4),
                'last_order': '2024-01-15'
            },
            {
                'rank': 2,
                'name': 'Entreprise ABC Premium',
                'total_orders': 72,
                'total_spent': int(total_sales * 0.3),
                'last_order': '2024-01-12'
            },
            {
                'rank': 3,
                'name': 'Société XYZ Elite',
                'total_orders': 68,
                'total_spent': int(total_sales * 0.2),
                'last_order': '2024-01-10'
            },
            {
                'rank': 4,
                'name': 'Groupe DEF Gold',
                'total_orders': 55,
                'total_spent': int(total_sales * 0.08),
                'last_order': '2024-01-08'
            },
            {
                'rank': 5,
                'name': 'Corporation GHI Platinum',
                'total_orders': 52,
                'total_spent': int(total_sales * 0.02),
                'last_order': '2024-01-05'
            }
        ]
    elif customer_segment == 'new':
        top_customers = [
            {
                'rank': 1,
                'name': 'Nouveau Client A',
                'total_orders': 3,
                'total_spent': int(total_sales * 0.3),
                'last_order': '2024-01-15'
            },
            {
                'rank': 2,
                'name': 'Nouveau Client B',
                'total_orders': 2,
                'total_spent': int(total_sales * 0.25),
                'last_order': '2024-01-12'
            },
            {
                'rank': 3,
                'name': 'Nouveau Client C',
                'total_orders': 2,
                'total_spent': int(total_sales * 0.2),
                'last_order': '2024-01-10'
            },
            {
                'rank': 4,
                'name': 'Nouveau Client D',
                'total_orders': 1,
                'total_spent': int(total_sales * 0.15),
                'last_order': '2024-01-08'
            },
            {
                'rank': 5,
                'name': 'Nouveau Client E',
                'total_orders': 1,
                'total_spent': int(total_sales * 0.1),
                'last_order': '2024-01-05'
            }
        ]
    else:
        # Tous les clients
        top_customers = [
            {
                'rank': 1,
                'name': 'SARL Tech Solutions',
                'total_orders': 45,
                'total_spent': int(total_sales * 0.32),
                'last_order': '2024-01-15'
            },
            {
                'rank': 2,
                'name': 'Entreprise ABC',
                'total_orders': 32,
                'total_spent': int(total_sales * 0.23),
                'last_order': '2024-01-12'
            },
            {
                'rank': 3,
                'name': 'Société XYZ',
                'total_orders': 28,
                'total_spent': int(total_sales * 0.21),
                'last_order': '2024-01-10'
            },
            {
                'rank': 4,
                'name': 'Groupe DEF',
                'total_orders': 25,
                'total_spent': int(total_sales * 0.15),
                'last_order': '2024-01-08'
            },
            {
                'rank': 5,
                'name': 'Corporation GHI',
                'total_orders': 22,
                'total_spent': int(total_sales * 0.09),
                'last_order': '2024-01-05'
            }
        ]
    
    # Top produits (ajusté selon la catégorie)
    if product_category == 'electronics':
        top_products = [
            {
                'rank': 1,
                'name': 'iPhone 15 Pro',
                'category': 'Électronique',
                'sales': int(total_sales * 0.4),
                'units_sold': 25,
                'image': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 2,
                'name': 'Samsung Galaxy S24',
                'category': 'Électronique',
                'sales': int(total_sales * 0.3),
                'units_sold': 18,
                'image': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 3,
                'name': 'MacBook Pro M3',
                'category': 'Électronique',
                'sales': int(total_sales * 0.2),
                'units_sold': 8,
                'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 4,
                'name': 'iPad Air',
                'category': 'Électronique',
                'sales': int(total_sales * 0.08),
                'units_sold': 15,
                'image': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 5,
                'name': 'AirPods Pro',
                'category': 'Électronique',
                'sales': int(total_sales * 0.02),
                'units_sold': 50,
                'image': 'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&h=400&fit=crop&crop=center'
            }
        ]
    elif product_category == 'clothing':
        top_products = [
            {
                'rank': 1,
                'name': 'Chemise Premium',
                'category': 'Vêtements',
                'sales': int(total_sales * 0.35),
                'units_sold': 120,
                'image': 'https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 2,
                'name': 'Jean Designer',
                'category': 'Vêtements',
                'sales': int(total_sales * 0.25),
                'units_sold': 80,
                'image': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 3,
                'name': 'Chaussures Cuir',
                'category': 'Chaussures',
                'sales': int(total_sales * 0.2),
                'units_sold': 45,
                'image': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 4,
                'name': 'Veste Sport',
                'category': 'Vêtements',
                'sales': int(total_sales * 0.15),
                'units_sold': 60,
                'image': 'https://images.unsplash.com/photo-1551028719-00167b6e7254?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 5,
                'name': 'Sac à Main',
                'category': 'Accessoires',
                'sales': int(total_sales * 0.05),
                'units_sold': 25,
                'image': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=400&fit=crop&crop=center'
            }
        ]
    elif product_category == 'sports':
        top_products = [
            {
                'rank': 1,
                'name': 'Nike Air Max',
                'category': 'Sport & Loisirs',
                'sales': int(total_sales * 0.4),
                'units_sold': 60,
                'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 2,
                'name': 'Adidas Ultraboost',
                'category': 'Sport & Loisirs',
                'sales': int(total_sales * 0.3),
                'units_sold': 40,
                'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 3,
                'name': 'Tapis de Yoga',
                'category': 'Équipements',
                'sales': int(total_sales * 0.15),
                'units_sold': 100,
                'image': 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 4,
                'name': 'Protéine Whey',
                'category': 'Nutrition',
                'sales': int(total_sales * 0.1),
                'units_sold': 200,
                'image': 'https://images.unsplash.com/photo-1593095948071-474c5cc2989d?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 5,
                'name': 'Montre Sport',
                'category': 'Accessoires',
                'sales': int(total_sales * 0.05),
                'units_sold': 15,
                'image': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop&crop=center'
            }
        ]
    else:
        # Toutes catégories
        top_products = [
            {
                'rank': 1,
                'name': 'iPhone 15 Pro',
                'category': 'Électronique',
                'sales': int(total_sales * 0.32),
                'units_sold': 25,
                'image': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 2,
                'name': 'Samsung Galaxy S24',
                'category': 'Électronique',
                'sales': int(total_sales * 0.23),
                'units_sold': 18,
                'image': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 3,
                'name': 'Nike Air Max',
                'category': 'Sport & Loisirs',
                'sales': int(total_sales * 0.15),
                'units_sold': 60,
                'image': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 4,
                'name': 'MacBook Pro M3',
                'category': 'Électronique',
                'sales': int(total_sales * 0.19),
                'units_sold': 8,
                'image': 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&h=400&fit=crop&crop=center'
            },
            {
                'rank': 5,
                'name': 'Adidas Ultraboost',
                'category': 'Sport & Loisirs',
                'sales': int(total_sales * 0.11),
                'units_sold': 40,
                'image': 'https://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=400&h=400&fit=crop&crop=center'
            }
        ]
    
    return {
        'kpis': kpis,
        'revenue_chart': revenue_chart,
        'sales_performance_chart': sales_performance_chart,
        'top_customers': top_customers,
        'top_products': top_products
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_main(request):
    """
    Endpoint principal - Données complètes des analytics
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        customer_segment = request.GET.get('customer_segment', 'all')
        product_category = request.GET.get('product_category', 'all')
        revenue_min = request.GET.get('revenue_min', 0)
        revenue_max = request.GET.get('revenue_max', 10000000)
        turnover_min = request.GET.get('turnover_min', 0)
        turnover_max = request.GET.get('turnover_max', 100)
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la clé de cache (inclure la company pour le cache)
        cache_params = {
            'period': period,
            'custom_start_date': custom_start_date,
            'custom_end_date': custom_end_date,
            'customer_segment': customer_segment,
            'product_category': product_category,
            'revenue_min': revenue_min,
            'revenue_max': revenue_max,
            'turnover_min': turnover_min,
            'turnover_max': turnover_max,
            'company_id': user_company.id if user_company else 'all'
        }
        cache_key = get_cache_key(cache_params)
        
        # Vérifier le cache
        cached_data = get_cached_data(cache_key, 'full_data')
        if cached_data:
            return Response(cached_data)
        
        # Générer les données réelles
        data = generate_real_data(start_date, end_date, user_company, customer_segment, product_category, revenue_min, revenue_max)
        
        # Mettre en cache (15 minutes pour les données complètes)
        set_cached_data(cache_key, 'full_data', data, 15)
        
        return Response(data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_kpis(request):
    """
    Endpoint spécifique - KPIs uniquement
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la clé de cache
        cache_params = {
            'period': period,
            'custom_start_date': custom_start_date,
            'custom_end_date': custom_end_date,
            'type': 'kpis',
            'company_id': user_company.id if user_company else 'all'
        }
        cache_key = get_cache_key(cache_params)
        
        # Vérifier le cache
        cached_data = get_cached_data(cache_key, 'kpis')
        if cached_data:
            return Response(cached_data)
        
        # Générer les données KPIs réelles
        data = generate_real_data(start_date, end_date, user_company, 'all', 'all', 0, 10000000)
        kpis_data = data['kpis']
        
        # Mettre en cache (5 minutes pour les KPIs)
        set_cached_data(cache_key, 'kpis', kpis_data, 5)
        
        return Response(kpis_data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_revenue_chart(request):
    """
    Endpoint spécifique - Graphique des revenus
    """
    try:
        # Accès libre pour tous les utilisateurs authentifiés
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la clé de cache
        cache_params = {
            'period': period,
            'custom_start_date': custom_start_date,
            'custom_end_date': custom_end_date,
            'type': 'revenue_chart'
        }
        cache_key = get_cache_key(cache_params)
        
        # Vérifier le cache
        cached_data = get_cached_data(cache_key, 'revenue_chart')
        if cached_data:
            return Response(cached_data)
        
        # Générer les données du graphique
        data = generate_sample_data(start_date, end_date, 'all', 'all', 0, 10000000)
        chart_data = data['revenue_chart']
        
        # Mettre en cache (10 minutes pour les graphiques)
        set_cached_data(cache_key, 'revenue_chart', chart_data, 10)
        
        return Response(chart_data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_sales_performance(request):
    """
    Endpoint spécifique - Performance des ventes
    """
    try:
        # Accès libre pour tous les utilisateurs authentifiés
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la clé de cache
        cache_params = {
            'period': period,
            'custom_start_date': custom_start_date,
            'custom_end_date': custom_end_date,
            'type': 'sales_performance'
        }
        cache_key = get_cache_key(cache_params)
        
        # Vérifier le cache
        cached_data = get_cached_data(cache_key, 'sales_performance')
        if cached_data:
            return Response(cached_data)
        
        # Générer les données de performance
        data = generate_sample_data(start_date, end_date, 'all', 'all', 0, 10000000)
        performance_data = data['sales_performance_chart']
        
        # Mettre en cache (10 minutes pour les graphiques)
        set_cached_data(cache_key, 'sales_performance', performance_data, 10)
        
        return Response(performance_data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_top_customers(request):
    """
    Endpoint spécifique - Top clients
    """
    try:
        # Accès libre pour tous les utilisateurs authentifiés
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        customer_segment = request.GET.get('customer_segment', 'all')
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la clé de cache
        cache_params = {
            'period': period,
            'custom_start_date': custom_start_date,
            'custom_end_date': custom_end_date,
            'customer_segment': customer_segment,
            'type': 'top_customers'
        }
        cache_key = get_cache_key(cache_params)
        
        # Vérifier le cache
        cached_data = get_cached_data(cache_key, 'top_customers')
        if cached_data:
            return Response(cached_data)
        
        # Générer les données des top clients
        data = generate_sample_data(start_date, end_date, customer_segment, 'all', 0, 10000000)
        customers_data = data['top_customers']
        
        # Mettre en cache (15 minutes pour les tableaux)
        set_cached_data(cache_key, 'top_customers', customers_data, 15)
        
        return Response(customers_data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analytics_top_products(request):
    """
    Endpoint spécifique - Top produits
    """
    try:
        # Accès libre pour tous les utilisateurs authentifiés
        
        # Récupérer les paramètres
        period = request.GET.get('period', '30d')
        custom_start_date = request.GET.get('custom_start_date')
        custom_end_date = request.GET.get('custom_end_date')
        product_category = request.GET.get('product_category', 'all')
        
        # Valider les paramètres
        try:
            start_date, end_date = get_date_range(period, custom_start_date, custom_end_date)
        except ValueError as e:
            return Response({
                'error': {
                    'code': 'INVALID_PERIOD',
                    'message': str(e),
                    'details': {
                        'field': 'period',
                        'value': period
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Créer la clé de cache
        cache_params = {
            'period': period,
            'custom_start_date': custom_start_date,
            'custom_end_date': custom_end_date,
            'product_category': product_category,
            'type': 'top_products'
        }
        cache_key = get_cache_key(cache_params)
        
        # Vérifier le cache
        cached_data = get_cached_data(cache_key, 'top_products')
        if cached_data:
            return Response(cached_data)
        
        # Générer les données des top produits
        data = generate_sample_data(start_date, end_date, 'all', product_category, 0, 10000000)
        products_data = data['top_products']
        
        # Mettre en cache (15 minutes pour les tableaux)
        set_cached_data(cache_key, 'top_products', products_data, 15)
        
        return Response(products_data)
        
    except Exception as e:
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'Erreur interne du serveur',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
