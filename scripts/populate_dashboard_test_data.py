#!/usr/bin/env python3
"""
Script pour remplir la base de données avec des données de test pour le dashboard
Ce script crée des données massives pour tester toutes les APIs du dashboard
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.utils import timezone

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings.local')
django.setup()

from django.contrib.auth.models import User
from apps.customers.models import Customer
from apps.inventory.models import Category, Product, ProductVariant
from apps.sales.models import Order, OrderItem, Invoice, Payment
from apps.stock.models import StockMovement, StockAlert
from apps.common.models import PasswordResetCode

def clear_database():
    """Vide la base de données"""
    print("🗑️  Nettoyage de la base de données...")
    
    # Supprimer dans l'ordre pour éviter les erreurs de clés étrangères
    PasswordResetCode.objects.all().delete()
    Payment.objects.all().delete()
    Invoice.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    StockMovement.objects.all().delete()
    StockAlert.objects.all().delete()
    ProductVariant.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    Customer.objects.all().delete()
    
    print("✅ Base de données nettoyée")

def create_users():
    """Crée des utilisateurs de test"""
    print("👥 Création des utilisateurs...")
    
    users = []
    for i in range(1, 6):
        user, created = User.objects.get_or_create(
            username=f'user{i}',
            defaults={
                'email': f'user{i}@test.com',
                'first_name': f'User{i}',
                'last_name': 'Test',
                'is_active': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
        users.append(user)
    
    print(f"✅ {len(users)} utilisateurs créés")
    return users

def create_categories():
    """Crée des catégories de produits"""
    print("📂 Création des catégories...")
    
    categories = []
    category_names = [
        "Électronique", "Vêtements", "Maison & Jardin", "Sports", "Livre & Média",
        "Beauté & Santé", "Automobile", "Alimentation", "Jouets", "Informatique"
    ]
    
    for name in category_names:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={
                'description': f'Catégorie {name}',
                'is_active': True
            }
        )
        categories.append(category)
    
    print(f"✅ {len(categories)} catégories créées")
    return categories

def create_products(categories):
    """Crée des produits avec variantes"""
    print("📦 Création des produits...")
    
    products = []
    product_names = [
        "Smartphone", "Laptop", "T-shirt", "Jean", "Chaussures", "Sac à dos",
        "Livre", "DVD", "Parfum", "Crème", "Pneu", "Batterie", "Câble",
        "Écouteurs", "Souris", "Clavier", "Moniteur", "Imprimante", "Scanner",
        "Tablette", "Montre", "Bracelet", "Collier", "Bague", "Lunettes"
    ]
    
    for i, name in enumerate(product_names):
        category = random.choice(categories)
        
        product, created = Product.objects.get_or_create(
            name=f"{name} {i+1}",
            defaults={
                'category': category,
                'description': f'Description du produit {name} {i+1}',
                'cost_price': Decimal(str(random.uniform(10, 500))),
                'price': Decimal(str(random.uniform(20, 1000))),
                'sku': f"SKU-{name.upper()}-{i+1:03d}",
                'status': 'active'
            }
        )
        
        # Créer plusieurs variantes pour chaque produit
        for j in range(random.randint(1, 4)):
            variant, created = ProductVariant.objects.get_or_create(
                product=product,
                name=f"Variante {j+1}",
                defaults={
                    'sku': f"{product.sku}-V{j+1}",
                    'value': f"Option {j+1}",
                    'price_modifier': Decimal(str(random.uniform(-10, 50))),
                    'stock_quantity': random.randint(0, 100),
                    'is_active': True
                }
            )
        
        products.append(product)
    
    print(f"✅ {len(products)} produits créés avec variantes")
    return products

def create_customers():
    """Crée des clients"""
    print("👤 Création des clients...")
    
    customers = []
    first_names = ["Jean", "Marie", "Pierre", "Sophie", "Paul", "Julie", "Marc", "Claire", "Thomas", "Nathalie"]
    last_names = ["Dupont", "Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Moreau", "Simon"]
    
    for i in range(100):  # 100 clients
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        
        customer, created = Customer.objects.get_or_create(
            email=f"{first_name.lower()}.{last_name.lower()}{i}@test.com",
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'phone': f"0{random.randint(100000000, 999999999)}",
                'address': f"{random.randint(1, 999)} rue de la Paix",
                'city': random.choice(["Paris", "Lyon", "Marseille", "Toulouse", "Nice", "Nantes", "Strasbourg", "Montpellier"]),
                'postal_code': f"{random.randint(10000, 99999)}",
                'country': "France",
                'is_active': True
            }
        )
        customers.append(customer)
    
    print(f"✅ {len(customers)} clients créés")
    return customers

def create_orders(customers, products, users):
    """Crée des commandes"""
    print("🛒 Création des commandes...")
    
    orders = []
    statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    
    for i in range(200):  # 200 commandes
        customer = random.choice(customers)
        user = random.choice(users)
        status = random.choice(statuses)
        
        # Date aléatoire dans les 6 derniers mois
        created_at = timezone.now() - timedelta(days=random.randint(0, 180))
        
        order = Order.objects.create(
            customer=customer,
            user=user,
            order_number=f"ORD-{i+1:06d}",
            status=status,
            order_date=created_at,
            total_amount=Decimal('0.00'),
            tax_rate=Decimal('20.00'),
            created_at=created_at
        )
        
        # Ajouter des articles à la commande
        num_items = random.randint(1, 5)
        total_amount = Decimal('0.00')
        
        for _ in range(num_items):
            product = random.choice(products)
            variant = product.variants.first()
            if variant:
                quantity = random.randint(1, 10)
                unit_price = variant.final_price  # Utiliser final_price au lieu de price
                item_total = unit_price * quantity
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price
                )
                
                total_amount += item_total
        
        # Mettre à jour le total de la commande
        order.total_amount = total_amount
        order.save()
        
        orders.append(order)
    
    print(f"✅ {len(orders)} commandes créées")
    return orders

def create_invoices(orders, users):
    """Crée des factures"""
    print("🧾 Création des factures...")
    
    invoices = []
    statuses = ['draft', 'sent', 'paid', 'overdue', 'cancelled']
    
    for order in orders:
        if order.status in ['confirmed', 'shipped', 'delivered']:
            status = random.choice(statuses)
            user = random.choice(users)
            
            # Date de facture après la commande
            invoice_date = order.created_at + timedelta(days=random.randint(1, 30))
            
            invoice = Invoice.objects.create(
                order=order,
                user=user,
                invoice_number=f"INV-{order.id:06d}",
                status=status,
                invoice_date=invoice_date,
                due_date=invoice_date + timedelta(days=30),
                subtotal=order.subtotal,
                tax_rate=order.tax_rate,
                tax_amount=order.tax_amount,
                total_amount=order.total_amount,
                remaining_amount=order.total_amount if status != 'paid' else Decimal('0.00'),
                created_at=invoice_date
            )
            
            # Créer un paiement si la facture est payée
            if status == 'paid':
                Payment.objects.create(
                    invoice=invoice,
                    amount=order.total_amount,
                    payment_method=random.choice(['credit_card', 'bank_transfer', 'cash', 'check']),
                    payment_date=invoice_date,
                    user=user,
                    created_at=invoice_date
                )
            
            invoices.append(invoice)
    
    print(f"✅ {len(invoices)} factures créées")
    return invoices

def create_stock_movements(products, users):
    """Crée des mouvements de stock"""
    print("📦 Création des mouvements de stock...")
    
    movements = []
    movement_types = ['in', 'out', 'adjustment']
    
    for product in products:
        for variant in product.variants.all():
            user = random.choice(users)
            
            # Mouvements d'entrée
            for _ in range(random.randint(1, 3)):
                quantity = random.randint(10, 100)
                movement = StockMovement.objects.create(
                    product=product,
                    variant=variant,
                    movement_type='in',
                    quantity=quantity,
                    unit_cost=variant.product.cost_price,
                    total_cost=variant.product.cost_price * quantity,
                    reference=f"REC-{random.randint(1000, 9999)}",
                    notes='Réception stock',
                    user=user,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 90))
                )
                movements.append(movement)
            
            # Mouvements de sortie
            for _ in range(random.randint(1, 5)):
                if variant.stock_quantity > 0:
                    quantity = random.randint(1, min(variant.stock_quantity, 20))
                    movement = StockMovement.objects.create(
                        product=product,
                        variant=variant,
                        movement_type='out',
                        quantity=-quantity,  # Négatif pour sortie
                        unit_cost=variant.product.cost_price,
                        total_cost=variant.product.cost_price * quantity,
                        reference=f"VEN-{random.randint(1000, 9999)}",
                        notes='Vente',
                        user=user,
                        created_at=timezone.now() - timedelta(days=random.randint(0, 90))
                    )
                    movements.append(movement)
    
    print(f"✅ {len(movements)} mouvements de stock créés")
    return movements

def create_stock_alerts(products):
    """Crée des alertes de stock"""
    print("⚠️  Création des alertes de stock...")
    
    alerts = []
    
    for product in products:
        for variant in product.variants.all():
            # Créer des alertes pour les produits avec stock faible
            if variant.stock_quantity < 10:
                alert = StockAlert.objects.create(
                    product=product,
                    variant=variant,
                    current_quantity=variant.stock_quantity,
                    threshold_quantity=10,
                    alert_type='low_stock',
                    is_active=True,
                    is_resolved=False,
                    created_at=timezone.now() - timedelta(days=random.randint(0, 30))
                )
                alerts.append(alert)
    
    print(f"✅ {len(alerts)} alertes de stock créées")
    return alerts

def update_stock_quantities(products):
    """Met à jour les quantités de stock basées sur les mouvements"""
    print("🔄 Mise à jour des quantités de stock...")
    
    from django.db.models import Sum
    
    for product in products:
        for variant in product.variants.all():
            # Calculer la quantité actuelle basée sur les mouvements
            total_in = StockMovement.objects.filter(
                variant=variant,
                movement_type='in'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            total_out = StockMovement.objects.filter(
                variant=variant,
                movement_type='out'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            variant.stock_quantity = max(0, total_in - total_out)
            variant.save()
    
    print("✅ Quantités de stock mises à jour")

def main():
    """Fonction principale"""
    print("🚀 Démarrage du script de population de données de test...")
    
    try:
        # Nettoyer la base
        clear_database()
        
        # Créer les données
        users = create_users()
        categories = create_categories()
        products = create_products(categories)
        customers = create_customers()
        orders = create_orders(customers, products, users)
        invoices = create_invoices(orders, users)
        movements = create_stock_movements(products, users)
        alerts = create_stock_alerts(products)
        
        # Mettre à jour les quantités de stock
        update_stock_quantities(products)
        
        print("\n🎉 Base de données remplie avec succès !")
        print(f"📊 Résumé des données créées :")
        print(f"   - Utilisateurs : {len(users)}")
        print(f"   - Catégories : {len(categories)}")
        print(f"   - Produits : {len(products)}")
        print(f"   - Clients : {len(customers)}")
        print(f"   - Commandes : {len(orders)}")
        print(f"   - Factures : {len(invoices)}")
        print(f"   - Mouvements de stock : {len(movements)}")
        print(f"   - Alertes de stock : {len(alerts)}")
        
        print("\n🔗 URLs de test disponibles :")
        print("   - Dashboard complet : http://localhost:8000/api/dashboard/overview/")
        print("   - KPIs : http://localhost:8000/api/dashboard/kpis/")
        print("   - Graphique ventes : http://localhost:8000/api/dashboard/sales-chart/")
        print("   - Top produits : http://localhost:8000/api/dashboard/top-products/")
        print("   - Distribution clients : http://localhost:8000/api/dashboard/clients-distribution/")
        print("   - Alertes : http://localhost:8000/api/dashboard/alerts/")
        print("   - Commandes récentes : http://localhost:8000/api/dashboard/recent-orders/")
        print("   - Factures récentes : http://localhost:8000/api/dashboard/recent-invoices/")
        
    except Exception as e:
        print(f"❌ Erreur lors de la population : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
