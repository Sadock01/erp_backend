from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from apps.sales.models import Order, Invoice, OrderItem
from apps.stock.models import StockMovement, StockAlert
from apps.inventory.models import Product
from apps.customers.models import Customer
from apps.common.tenant_scope import get_user_company_or_all, add_company_filter


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_kpis(request):
    """
    Récupère les indicateurs clés de performance pour les 4 cartes principales du dashboard.
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        # Calculs des KPIs
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Filtrage par company si nécessaire
        order_filter = {}
        add_company_filter(order_filter, user_company, 'company')
        
        # KPIs Revenue
        revenue_today = Order.objects.filter(
            created_at__date=today,
            status__in=['confirmed', 'shipped', 'delivered'],
            **order_filter
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        revenue_week = Order.objects.filter(
            created_at__date__gte=week_ago,
            status__in=['confirmed', 'shipped', 'delivered'],
            **order_filter
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        revenue_month = Order.objects.filter(
            created_at__date__gte=month_ago,
            status__in=['confirmed', 'shipped', 'delivered'],
            **order_filter
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        # Calcul de la croissance (comparaison avec le mois précédent)
        previous_month_start = month_ago - timedelta(days=30)
        previous_month_revenue = Order.objects.filter(
            created_at__date__gte=previous_month_start,
            created_at__date__lt=month_ago,
            status__in=['confirmed', 'shipped', 'delivered'],
            **order_filter
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
        
        growth = 0.0
        if previous_month_revenue > 0:
            growth = float(((revenue_month - previous_month_revenue) / previous_month_revenue) * 100)
        
        # Filtrage par company pour les autres modèles
        invoice_filter = {}
        customer_filter = {}
        product_filter = {}
        stock_filter = {}
        add_company_filter(invoice_filter, user_company, 'company')
        add_company_filter(customer_filter, user_company, 'company')
        add_company_filter(product_filter, user_company, 'company')
        add_company_filter(stock_filter, user_company, 'company')
        
        # KPIs Orders
        orders_total = Order.objects.filter(**order_filter).count()
        orders_pending = Order.objects.filter(status='pending', **order_filter).count()
        orders_confirmed = Order.objects.filter(status='confirmed', **order_filter).count()
        orders_shipped = Order.objects.filter(status='shipped', **order_filter).count()
        orders_delivered = Order.objects.filter(status='delivered', **order_filter).count()
        
        # KPIs Invoices
        invoices_total = Invoice.objects.filter(**invoice_filter).count()
        invoices_paid = Invoice.objects.filter(status='paid', **invoice_filter).count()
        invoices_pending = Invoice.objects.filter(status='pending', **invoice_filter).count()
        invoices_overdue = Invoice.objects.filter(
            status='pending',
            due_date__lt=today,
            **invoice_filter
        ).count()
        
        invoices_total_amount = Invoice.objects.filter(**invoice_filter).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # KPIs Stock
        stock_movements = StockMovement.objects.filter(**stock_filter)
        stock_total_value = sum(
            movement.quantity * movement.unit_cost 
            for movement in stock_movements 
            if movement.movement_type == 'in'
        )
        
        products_count = Product.objects.filter(**product_filter).count()
        low_stock_alerts = StockAlert.objects.filter(
            alert_type='low_stock',
            is_active=True,
            **stock_filter
        ).count()
        
        from apps.inventory.models import ProductVariant
        out_of_stock = ProductVariant.objects.filter(
            stock_quantity__lte=0,
            **product_filter
        ).count()
        
        data = {
            "revenue": {
                "today": float(revenue_today),
                "week": float(revenue_week),
                "month": float(revenue_month),
                "growth": round(growth, 2)
            },
            "orders": {
                "total": orders_total,
                "pending": orders_pending,
                "confirmed": orders_confirmed,
                "shipped": orders_shipped,
                "delivered": orders_delivered
            },
            "invoices": {
                "total": invoices_total,
                "paid": invoices_paid,
                "pending": invoices_pending,
                "overdue": invoices_overdue,
                "total_amount": float(invoices_total_amount)
            },
            "stock": {
                "total_value": float(stock_total_value),
                "products_count": products_count,
                "low_stock_alerts": low_stock_alerts,
                "out_of_stock": out_of_stock
            }
        }
        
        return Response({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "DASHBOARD_ERROR",
                "message": "Erreur lors de la récupération des KPIs",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_sales_chart(request):
    """
    Données pour le graphique d'évolution des ventes (30 derniers jours par défaut).
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        days = int(request.GET.get('days', 30))
        period = request.GET.get('period', 'daily')
        
        # Filtrage par company si nécessaire
        order_filter = {}
        add_company_filter(order_filter, user_company, 'company')
        
        # Si period=month, afficher les 30 derniers jours
        if period == 'month':
            period = 'daily'
            days = 30
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Génération des labels selon la période
        labels = []
        if period == 'daily':
            current_date = start_date
            while current_date <= end_date:
                # Format: "1 Jan", "5 Jan", etc.
                labels.append(current_date.strftime('%d %b'))
                current_date += timedelta(days=1)
        elif period == 'weekly':
            # Groupement par semaine
            current_date = start_date
            while current_date <= end_date:
                week_end = min(current_date + timedelta(days=6), end_date)
                labels.append(f"{current_date.strftime('%Y-%m-%d')} - {week_end.strftime('%Y-%m-%d')}")
                current_date += timedelta(days=7)
        elif period == 'monthly':
            # Groupement par mois
            current_date = start_date.replace(day=1)
            while current_date <= end_date:
                labels.append(current_date.strftime('%Y-%m'))
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # Calcul des données de vente
        sales_data = []
        if period == 'daily':
            for i, label in enumerate(labels):
                date = start_date + timedelta(days=i)
                # Utiliser order_date__range pour capturer toute la journée
                day_start = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
                day_end = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))
                
                daily_revenue = Order.objects.filter(
                    order_date__range=[day_start, day_end],
                    status__in=['confirmed', 'shipped', 'delivered'],
                    **order_filter
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                sales_data.append(float(daily_revenue))
                # Debug: afficher les données pour les jours avec des ventes
                if float(daily_revenue) > 0:
                    print(f"Jour {date}: {daily_revenue} FCFA")
        elif period == 'weekly':
            for i, label in enumerate(labels):
                week_start = start_date + timedelta(days=i*7)
                week_end = min(week_start + timedelta(days=6), end_date)
                weekly_revenue = Order.objects.filter(
                    order_date__date__gte=week_start,
                    order_date__date__lte=week_end,
                    status__in=['confirmed', 'shipped', 'delivered'],
                    **order_filter
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                sales_data.append(float(weekly_revenue))
        elif period == 'monthly':
            for i, label in enumerate(labels):
                month_start = start_date.replace(day=1) + timedelta(days=i*30)
                if month_start.month == 12:
                    month_end = month_start.replace(year=month_start.year + 1, month=1) - timedelta(days=1)
                else:
                    month_end = month_start.replace(month=month_start.month + 1) - timedelta(days=1)
                
                monthly_revenue = Order.objects.filter(
                    order_date__date__gte=month_start,
                    order_date__date__lte=month_end,
                    status__in=['confirmed', 'shipped', 'delivered'],
                    **order_filter
                ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
                sales_data.append(float(monthly_revenue))
        
        # Calcul du résumé
        total_revenue = sum(sales_data)
        average_revenue = total_revenue / len(sales_data) if sales_data else 0
        
        # Calcul de la croissance
        if len(sales_data) >= 2:
            first_half = sales_data[:len(sales_data)//2]
            second_half = sales_data[len(sales_data)//2:]
            first_avg = sum(first_half) / len(first_half) if first_half else 0
            second_avg = sum(second_half) / len(second_half) if second_half else 0
            growth = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        else:
            growth = 0
        
        trend = "up" if growth > 0 else "down" if growth < 0 else "stable"
        
        data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Chiffre d'affaires (FCFA)",
                    "data": sales_data,
                    "period": period,
                    "currency": "XOF"
                }
            ],
            "summary": {
                "total": round(total_revenue, 2),
                "average": round(average_revenue, 2),
                "growth": round(growth, 2),
                "trend": trend,
                "currency": "XOF"
            },
            "period_info": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "period_type": period,
                "total_days": days
            }
        }
        
        return Response({
            "success": True,
            "data": data,
            "message": "Données des ventes récupérées avec succès"
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "SALES_CHART_ERROR",
                "message": "Erreur lors de la récupération du graphique des ventes",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_products_chart(request):
    """
    Données pour le graphique des produits les plus vendus.
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        limit = int(request.GET.get('limit', 8))
        period = request.GET.get('period', 'month')
        
        # Filtrage par company si nécessaire
        order_filter = {}
        add_company_filter(order_filter, user_company, 'company')
        
        # Calcul de la période
        end_date = timezone.now().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Récupération des produits les plus vendus
        order_items_filter = {
            'order__created_at__date__gte': start_date,
            'order__status__in': ['confirmed', 'shipped', 'delivered']
        }
        add_company_filter(order_items_filter, user_company, 'order__company')
            
        top_products = OrderItem.objects.filter(**order_items_filter).values(
            'product__name',
            'product__id'
        ).annotate(
            total_quantity=Sum('quantity')
        ).order_by('-total_quantity')[:limit]
        
        labels = []
        data = []
        total_units = 0
        total_revenue = 0
        
        for product in top_products:
            labels.append(product['product__name'])
            quantity = product['total_quantity']
            data.append(quantity)
            total_units += quantity
            
            # Calcul du revenu pour ce produit
            product_revenue_filter = {
                'product_id': product['product__id'],
                'order__created_at__date__gte': start_date,
                'order__status__in': ['confirmed', 'shipped', 'delivered']
            }
            add_company_filter(product_revenue_filter, user_company, 'order__company')
                
            product_revenue = OrderItem.objects.filter(**product_revenue_filter).aggregate(
                revenue=Sum(F('quantity') * F('unit_price'))
            )['revenue'] or Decimal('0.00')
            total_revenue += float(product_revenue)
        
        top_product = labels[0] if labels else ""
        top_sales = data[0] if data else 0
        
        response_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "Ventes (unités)",
                    "data": data
                }
            ],
            "summary": {
                "total_units": total_units,
                "total_revenue": round(total_revenue, 2),
                "top_product": top_product,
                "top_sales": top_sales
            }
        }
        
        return Response({
            "success": True,
            "data": response_data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "PRODUCTS_CHART_ERROR",
                "message": "Erreur lors de la récupération du graphique des produits",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_clients_chart(request):
    """
    Données pour le graphique de répartition des clients par catégorie.
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        # Filtrage par company si nécessaire
        customer_filter = {}
        add_company_filter(customer_filter, user_company, 'company')
        
        # Calcul des catégories de clients
        total_clients = Customer.objects.filter(**customer_filter).count()
        
        # Nouveaux clients (créés dans les 30 derniers jours)
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        new_clients_filter = {
            'created_at__date__gte': thirty_days_ago
        }
        add_company_filter(new_clients_filter, user_company, 'company')
        new_clients = Customer.objects.filter(**new_clients_filter).count()
        
        # Clients existants (créés avant les 30 derniers jours)
        existing_clients = total_clients - new_clients
        
        # Clients VIP (avec plus de 5 commandes)
        vip_clients_filter = {}
        add_company_filter(vip_clients_filter, user_company, 'company')
        vip_clients = Customer.objects.filter(**vip_clients_filter).annotate(
            orders_count=Count('order')
        ).filter(orders_count__gte=5).count()
        
        # Clients inactifs (pas de commande dans les 90 derniers jours)
        ninety_days_ago = timezone.now().date() - timedelta(days=90)
        inactive_clients_filter = {
            'order__isnull': True
        }
        add_company_filter(inactive_clients_filter, user_company, 'company')
        inactive_clients = Customer.objects.filter(**inactive_clients_filter).count()
        
        # Ajustement pour éviter les doublons
        if inactive_clients > total_clients:
            inactive_clients = max(0, total_clients - new_clients - existing_clients)
        
        data = [new_clients, existing_clients, vip_clients, inactive_clients]
        labels = [
            "Nouveaux clients",
            "Clients existants", 
            "Clients VIP",
            "Clients inactifs"
        ]
        
        response_data = {
            "labels": labels,
            "datasets": [
                {
                    "data": data,
                    "total": total_clients
                }
            ],
            "summary": {
                "total_clients": total_clients,
                "new_clients": new_clients,
                "existing_clients": existing_clients,
                "vip_clients": vip_clients,
                "inactive_clients": inactive_clients
            }
        }
        
        return Response({
            "success": True,
            "data": response_data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "CLIENTS_CHART_ERROR",
                "message": "Erreur lors de la récupération du graphique des clients",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_alerts(request):
    """
    Récupère les alertes importantes nécessitant l'attention de l'utilisateur.
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        limit = int(request.GET.get('limit', 10))
        priority = request.GET.get('priority', 'all')
        
        # Filtrage par company si nécessaire
        stock_filter = {}
        order_filter = {}
        invoice_filter = {}
        add_company_filter(stock_filter, user_company, 'company')
        add_company_filter(order_filter, user_company, 'company')
        add_company_filter(invoice_filter, user_company, 'company')
        
        alerts = []
        
        # Alertes de stock bas
        low_stock_alerts = StockAlert.objects.filter(
            alert_type='low_stock',
            is_active=True,
            **stock_filter
        )[:5]
        
        for alert in low_stock_alerts:
            stock_quantity = alert.product.get_stock_quantity()
            alerts.append({
                "id": f"stock_{alert.id}",
                "type": "warning",
                "title": "Stock bas",
                "message": f"{alert.product.name} - Stock bas ({stock_quantity} unités restantes)",
                "priority": "high",
                "time": alert.created_at.isoformat(),
                "action_url": f"/inventory/products/{alert.product.id}/",
                "action_label": "Voir le produit",
                "created_at": alert.created_at.isoformat()
            })
        
        # Alertes de factures en retard
        overdue_invoices = Invoice.objects.filter(
            status='pending',
            due_date__lt=timezone.now().date(),
            **invoice_filter
        )[:5]
        
        for invoice in overdue_invoices:
            days_overdue = (timezone.now().date() - invoice.due_date).days
            alerts.append({
                "id": f"invoice_{invoice.id}",
                "type": "error",
                "title": "Facture en retard",
                "message": f"Facture #{invoice.invoice_number} - Échéance dépassée de {days_overdue} jours",
                "priority": "high",
                "time": invoice.due_date.isoformat(),
                "action_url": f"/sales/invoices/{invoice.id}/",
                "action_label": "Voir la facture",
                "created_at": invoice.created_at.isoformat()
            })
        
        # Alertes de commandes en attente
        pending_orders = Order.objects.filter(
            status='pending',
            **order_filter
        ).order_by('-created_at')[:5]
        
        for order in pending_orders:
            alerts.append({
                "id": f"order_{order.id}",
                "type": "info",
                "title": "Commande en attente",
                "message": f"Commande #{order.order_number} - En attente de validation",
                "priority": "medium",
                "time": order.created_at.isoformat(),
                "action_url": f"/sales/orders/{order.id}/",
                "action_label": "Valider",
                "created_at": order.created_at.isoformat()
            })
        
        # Filtrage par priorité si demandé
        if priority != 'all':
            priority_map = {'high': 'high', 'medium': 'medium', 'low': 'low'}
            if priority in priority_map:
                alerts = [alert for alert in alerts if alert['priority'] == priority_map[priority]]
        
        # Tri par priorité et date
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        alerts.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['time']), reverse=True)
        
        # Limitation du nombre d'alertes
        alerts = alerts[:limit]
        
        # Calcul du résumé - total de toutes les alertes, pas seulement celles retournées
        total_stock_alerts = StockAlert.objects.filter(is_active=True, **stock_filter).count()
        total_overdue_invoices = Invoice.objects.filter(
            status='pending',
            due_date__lt=timezone.now().date(),
            **invoice_filter
        ).count()
        total_pending_orders = Order.objects.filter(status='pending', **order_filter).count()
        total_all_alerts = total_stock_alerts + total_overdue_invoices + total_pending_orders
        
        summary = {
            "total": total_all_alerts,
            "high_priority": len([a for a in alerts if a['priority'] == 'high']),
            "medium_priority": len([a for a in alerts if a['priority'] == 'medium']),
            "low_priority": len([a for a in alerts if a['priority'] == 'low'])
        }
        
        return Response({
            "success": True,
            "data": alerts,
            "summary": summary
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "ALERTS_ERROR",
                "message": "Erreur lors de la récupération des alertes",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_recent_orders(request):
    """
    Récupère les dernières commandes créées pour le tableau du dashboard.
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        limit = int(request.GET.get('limit', 10))
        status_filter = request.GET.get('status', None)
        
        # Filtrage par company si nécessaire
        order_filter = {}
        add_company_filter(order_filter, user_company, 'company')
        
        # Filtrage des commandes
        orders_query = Order.objects.select_related('customer').filter(**order_filter).order_by('-created_at')
        
        if status_filter:
            orders_query = orders_query.filter(status=status_filter)
        
        recent_orders = orders_query[:limit]
        
        orders_data = []
        total_amount = 0
        status_breakdown = {}
        
        for order in recent_orders:
            orders_data.append({
                "id": order.order_number,
                "customer": f"{order.customer.first_name} {order.customer.last_name}" if order.customer else "Client inconnu",
                "amount": float(order.total_amount),
                "status": order.status,
                "date": order.created_at.isoformat(),
                "currency": "EUR"
            })
            
            total_amount += float(order.total_amount)
            status_breakdown[order.status] = status_breakdown.get(order.status, 0) + 1
        
        # Calculer le total de toutes les commandes (pas seulement celles retournées)
        total_orders_count = Order.objects.filter(**order_filter).count()
        
        summary = {
            "total": total_orders_count,
            "total_amount": round(total_amount, 2),
            "status_breakdown": status_breakdown
        }
        
        return Response({
            "success": True,
            "data": orders_data,
            "summary": summary
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "RECENT_ORDERS_ERROR",
                "message": "Erreur lors de la récupération des commandes récentes",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_recent_invoices(request):
    """
    Récupère les dernières factures générées pour le tableau du dashboard.
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        limit = int(request.GET.get('limit', 10))
        status_filter = request.GET.get('status', None)
        
        # Filtrage par company si nécessaire
        invoice_filter = {}
        add_company_filter(invoice_filter, user_company, 'company')
        
        # Filtrage des factures
        invoices_query = Invoice.objects.select_related('order__customer', 'user').filter(**invoice_filter).order_by('-created_at')
        
        if status_filter:
            invoices_query = invoices_query.filter(status=status_filter)
        
        recent_invoices = invoices_query[:limit]
        
        invoices_data = []
        total_amount = 0
        status_breakdown = {}
        
        for invoice in recent_invoices:
            invoices_data.append({
                "id": invoice.invoice_number,
                "customer": f"{invoice.order.customer.first_name} {invoice.order.customer.last_name}" if invoice.order.customer else "Client inconnu",
                "amount": float(invoice.total_amount),
                "status": invoice.status,
                "due_date": invoice.due_date.isoformat(),
                "created_at": invoice.created_at.isoformat(),
                "currency": "EUR"
            })
            
            total_amount += float(invoice.total_amount)
            status_breakdown[invoice.status] = status_breakdown.get(invoice.status, 0) + 1
        
        # Calculer le total de toutes les factures (pas seulement celles retournées)
        total_invoices_count = Invoice.objects.filter(**invoice_filter).count()
        
        summary = {
            "total": total_invoices_count,
            "total_amount": round(total_amount, 2),
            "status_breakdown": status_breakdown
        }
        
        return Response({
            "success": True,
            "data": invoices_data,
            "summary": summary
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "RECENT_INVOICES_ERROR",
                "message": "Erreur lors de la récupération des factures récentes",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_all(request):
    """
    Récupère toutes les données du dashboard en une seule requête (optimisation).
    """
    try:
        # Obtenir la company de l'utilisateur (ou None si Super Admin)
        user_company = get_user_company_or_all(request.user)
        
        # Récupération directe des données sans passer par les autres vues
        
        # KPIs
        kpis_data = _get_kpis_data(user_company)
        
        # Graphiques
        sales_chart_data = _get_sales_chart_data(user_company)
        products_chart_data = _get_products_chart_data(user_company)
        clients_chart_data = _get_clients_chart_data(user_company)
        
        # Alertes
        alerts_data = _get_alerts_data(user_company)
        
        # Données récentes
        recent_orders_data = _get_recent_orders_data(user_company)
        recent_invoices_data = _get_recent_invoices_data(user_company)
        
        data = {
            "kpis": kpis_data,
            "sales_chart": sales_chart_data,
            "products_chart": products_chart_data,
            "clients_chart": clients_chart_data,
            "alerts": alerts_data,
            "recent_orders": recent_orders_data,
            "recent_invoices": recent_invoices_data
        }
        
        return Response({
            "success": True,
            "data": data
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": {
                "code": "DASHBOARD_ALL_ERROR",
                "message": "Erreur lors de la récupération de toutes les données du dashboard",
                "details": str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Fonctions helper privées pour dashboard_all
def _get_kpis_data(user_company=None):
    """Récupère les données des KPIs"""
    try:
        # Filtrage par company si nécessaire
        order_filter = {}
        customer_filter = {}
        stock_filter = {}
        add_company_filter(order_filter, user_company, 'company')
        add_company_filter(customer_filter, user_company, 'company')
        add_company_filter(stock_filter, user_company, 'company')
        
        # Commandes
        total_orders = Order.objects.filter(**order_filter).count()
        total_revenue = Order.objects.filter(**order_filter).aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        # Clients
        from apps.customers.models import Customer
        total_customers = Customer.objects.filter(**customer_filter).count()
        
        # Alertes stock
        from apps.stock.models import StockAlert
        low_stock_alerts = StockAlert.objects.filter(
            current_quantity__lte=F('threshold_quantity'),
            **stock_filter
        ).count()
        
        return {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "total_customers": total_customers,
            "low_stock_alerts": low_stock_alerts
        }
    except Exception:
        return {
            "total_orders": 0,
            "total_revenue": 0.0,
            "total_customers": 0,
            "low_stock_alerts": 0
        }


def _get_sales_chart_data(user_company=None):
    """Récupère les données du graphique des ventes"""
    try:
        from datetime import timedelta
        from django.db.models import Sum
        
        # Filtrage par company si nécessaire
        order_filter = {}
        add_company_filter(order_filter, user_company, 'company')
        
        # Données des 30 derniers jours
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        daily_sales = []
        labels = []
        
        for i in range(30):
            day_start = start_date + timedelta(days=i)
            day_end = day_start + timedelta(days=1)
            
            # Utiliser order_date au lieu de created_at
            sales = Order.objects.filter(
                order_date__range=[day_start, day_end],
                status__in=['confirmed', 'shipped', 'delivered'],
                **order_filter
            ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
            
            daily_sales.append(float(sales))
            labels.append(day_start.strftime('%d %b'))
        
        # Calculer les totaux et la croissance
        total_sales = sum(daily_sales)
        average_sales = total_sales / len(daily_sales) if daily_sales else 0
        
        # Calculer la croissance (comparaison avec les 15 premiers jours vs 15 derniers jours)
        if len(daily_sales) >= 30:
            previous_period = sum(daily_sales[:15])  # 15 premiers jours
            current_period = sum(daily_sales[15:])   # 15 derniers jours
            growth = ((current_period - previous_period) / previous_period * 100) if previous_period > 0 else 0
        else:
            growth = 0
        
        # Déterminer la tendance
        if growth > 5:
            trend = "up"
        elif growth < -5:
            trend = "down"
        else:
            trend = "stable"
        
        return {
            "labels": labels,
            "datasets": [{
                "label": "Chiffre d'affaires (FCFA)",
                "data": daily_sales,
                "period": "daily",
                "currency": "XOF"
            }],
            "summary": {
                "total": round(total_sales, 2),
                "average": round(average_sales, 2),
                "growth": round(growth, 2),
                "trend": trend,
                "currency": "XOF"
            },
            "period_info": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "period_type": "daily",
                "total_days": 30
            }
        }
    except Exception as e:
        return {
            "labels": [f"{i+1:02d}/01" for i in range(30)],
            "datasets": [{
                "label": "Chiffre d'affaires (FCFA)",
                "data": [0] * 30,
                "period": "month"
            }],
            "summary": {
                "total": 0,
                "average": 0,
                "growth": 0,
                "trend": "stable"
            }
        }


def _get_products_chart_data(user_company=None):
    """Récupère les données du graphique des produits"""
    try:
        from apps.inventory.models import ProductVariant
        from django.db.models import Sum

        pv_filter = {}
        add_company_filter(pv_filter, user_company, 'company')
        top_products = ProductVariant.objects.filter(**pv_filter).annotate(
            total_sold=Sum('orderitem__quantity')
        ).filter(total_sold__gt=0).order_by('-total_sold')[:4]
        
        labels = [product.product.name for product in top_products]
        data = [float(product.total_sold or 0) for product in top_products]
        
        return {
            "labels": labels,
            "datasets": [{
                "label": "Quantité vendue",
                "data": data,
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 205, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)"
                ]
            }]
        }
    except Exception:
        return {
            "labels": ["Produit A", "Produit B", "Produit C", "Produit D"],
            "datasets": [{
                "label": "Quantité vendue",
                "data": [0, 0, 0, 0],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.2)",
                    "rgba(54, 162, 235, 0.2)",
                    "rgba(255, 205, 86, 0.2)",
                    "rgba(75, 192, 192, 0.2)"
                ]
            }]
        }


def _get_clients_chart_data(user_company=None):
    """Récupère les données du graphique des clients"""
    try:
        from apps.customers.models import Customer
        from datetime import timedelta
        from django.db.models import Sum

        cf = {}
        add_company_filter(cf, user_company, 'company')
        
        # Clients nouveaux (derniers 30 jours)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        new_customers = Customer.objects.filter(created_at__gte=thirty_days_ago, **cf).count()
        
        # Clients existants (créés il y a plus de 30 jours)
        existing_customers = Customer.objects.filter(created_at__lt=thirty_days_ago, **cf).count()
        
        # Clients VIP (avec commandes totales > 1000€)
        vip_customers = Customer.objects.filter(**cf).annotate(
            total_spent=Sum('order__total_amount')
        ).filter(total_spent__gt=1000).count()
        
        # Clients inactifs (créés il y a plus de 90 jours sans commande récente)
        ninety_days_ago = timezone.now() - timedelta(days=90)
        inactive_customers = Customer.objects.filter(
            created_at__lt=ninety_days_ago,
            **cf
        ).exclude(
            order__created_at__gte=thirty_days_ago
        ).distinct().count()
        
        return {
            "labels": ["Nouveaux clients", "Clients existants", "Clients VIP", "Clients inactifs"],
            "datasets": [{
                "data": [new_customers, existing_customers, vip_customers, inactive_customers]
            }],
            "total": new_customers + existing_customers + vip_customers + inactive_customers
        }
    except Exception:
        return {
            "labels": ["Nouveaux clients", "Clients existants", "Clients VIP", "Clients inactifs"],
            "datasets": [{
                "data": [0, 0, 0, 0]
            }],
            "total": 0
        }


def _get_alerts_data(user_company=None):
    """Récupère les données des alertes"""
    try:
        from apps.stock.models import StockAlert

        sf = {}
        add_company_filter(sf, user_company, 'company')
        alerts = StockAlert.objects.filter(
            current_quantity__lte=F('threshold_quantity'),
            **sf
        ).select_related('variant__product')[:10]
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                "id": alert.id,
                "type": "stock",
                "title": "Stock faible",
                "message": f"{alert.variant.product.name} - Seulement {alert.current_quantity} unités restantes",
                "priority": "high",
                "created_at": alert.created_at.isoformat()
            })
        
        return alerts_data
    except Exception:
        return []


def _get_recent_orders_data(user_company=None):
    """Récupère les données des commandes récentes"""
    try:
        of = {}
        add_company_filter(of, user_company, 'company')
        recent_orders = Order.objects.filter(**of).select_related('customer').order_by('-created_at')[:5]
        
        orders_data = []
        for order in recent_orders:
            orders_data.append({
                "id": order.id,
                "order_number": order.order_number,
                "customer_name": f"{order.customer.first_name} {order.customer.last_name}" if order.customer else "Client inconnu",
                "total_amount": float(order.total_amount),
                "status": order.status,
                "created_at": order.created_at.isoformat()
            })
        
        return orders_data
    except Exception:
        return []


def _get_recent_invoices_data(user_company=None):
    """Récupère les données des factures récentes"""
    try:
        invf = {}
        add_company_filter(invf, user_company, 'company')
        recent_invoices = Invoice.objects.filter(**invf).select_related('order__customer').order_by('-created_at')[:5]
        
        invoices_data = []
        for invoice in recent_invoices:
            invoices_data.append({
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "customer_name": f"{invoice.order.customer.first_name} {invoice.order.customer.last_name}" if invoice.order and invoice.order.customer else "Client inconnu",
                "total_amount": float(invoice.total_amount),
                "status": invoice.status,
                "created_at": invoice.created_at.isoformat()
            })
        
        return invoices_data
    except Exception:
        return []
