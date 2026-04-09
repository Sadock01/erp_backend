#!/usr/bin/env python3
"""
Script de remplissage de la base de données Nodus ERP
Génère des données de test pour le dashboard et tous les modules
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from apps.customers.models import Customer
from apps.inventory.models import Category, Product, ProductVariant
from apps.stock.models import StockMovement, StockAlert
from apps.sales.models import Order, OrderItem, Invoice, Payment
from apps.permissions.models import Role, UserRole, RolePermission

def create_users_and_roles():
    """Créer des utilisateurs et des rôles"""
    print("👥 Création des utilisateurs et rôles...")
    
    # Créer un super utilisateur
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@nodus-erp.com',
            password='admin123',
            first_name='Admin',
            last_name='Nodus'
        )
        print("✅ Super utilisateur 'admin' créé")
    
    # Créer des utilisateurs de test
    users_data = [
        {'username': 'manager', 'first_name': 'Marie', 'last_name': 'Dupont', 'email': 'manager@baobab-erp.com'},
        {'username': 'sales1', 'first_name': 'Jean', 'last_name': 'Martin', 'email': 'sales1@baobab-erp.com'},
        {'username': 'sales2', 'first_name': 'Sophie', 'last_name': 'Bernard', 'email': 'sales2@baobab-erp.com'},
        {'username': 'stock1', 'first_name': 'Pierre', 'last_name': 'Durand', 'email': 'stock1@baobab-erp.com'},
        {'username': 'viewer', 'first_name': 'Alice', 'last_name': 'Moreau', 'email': 'viewer@baobab-erp.com'},
    ]
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='password123',
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            print(f"✅ Utilisateur '{user_data['username']}' créé")
    
    # Créer des rôles
    roles_data = [
        {'name': 'Super Admin', 'description': 'Accès complet au système'},
        {'name': 'Manager', 'description': 'Gestionnaire avec accès aux rapports'},
        {'name': 'Sales', 'description': 'Commercial'},
        {'name': 'Stock Manager', 'description': 'Gestionnaire de stock'},
        {'name': 'Viewer', 'description': 'Consultation seule'},
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        if created:
            print(f"✅ Rôle '{role_data['name']}' créé")
    
    # Assigner des rôles aux utilisateurs
    role_assignments = [
        ('admin', 'Super Admin'),
        ('manager', 'Manager'),
        ('sales1', 'Sales'),
        ('sales2', 'Sales'),
        ('stock1', 'Stock Manager'),
        ('viewer', 'Viewer'),
    ]
    
    for username, role_name in role_assignments:
        user = User.objects.get(username=username)
        role = Role.objects.get(name=role_name)
        UserRole.objects.get_or_create(user=user, role=role)
        print(f"✅ Rôle '{role_name}' assigné à '{username}'")


def create_customers():
    """Créer des clients"""
    print("👥 Création des clients...")
    
    customers_data = [
        {'first_name': 'Jean', 'last_name': 'Dupont', 'email': 'jean.dupont@email.com', 'phone': '0123456789'},
        {'first_name': 'Marie', 'last_name': 'Martin', 'email': 'marie.martin@email.com', 'phone': '0123456790'},
        {'first_name': 'Pierre', 'last_name': 'Durand', 'email': 'pierre.durand@email.com', 'phone': '0123456791'},
        {'first_name': 'Sophie', 'last_name': 'Bernard', 'email': 'sophie.bernard@email.com', 'phone': '0123456792'},
        {'first_name': 'Paul', 'last_name': 'Moreau', 'email': 'paul.moreau@email.com', 'phone': '0123456793'},
        {'first_name': 'Alice', 'last_name': 'Petit', 'email': 'alice.petit@email.com', 'phone': '0123456794'},
        {'first_name': 'Robert', 'last_name': 'Roux', 'email': 'robert.roux@email.com', 'phone': '0123456795'},
        {'first_name': 'Claire', 'last_name': 'Simon', 'email': 'claire.simon@email.com', 'phone': '0123456796'},
        {'first_name': 'Michel', 'last_name': 'Laurent', 'email': 'michel.laurent@email.com', 'phone': '0123456797'},
        {'first_name': 'Nathalie', 'last_name': 'Lefebvre', 'email': 'nathalie.lefebvre@email.com', 'phone': '0123456798'},
    ]
    
    for customer_data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=customer_data['email'],
            defaults={
                'first_name': customer_data['first_name'],
                'last_name': customer_data['last_name'],
                'phone': customer_data['phone'],
                'address': f"{random.randint(1, 100)} Rue de la Paix, 75001 Paris",
                'city': 'Paris',
                'postal_code': '75001',
                'country': 'France'
            }
        )
        if created:
            print(f"✅ Client '{customer_data['first_name']} {customer_data['last_name']}' créé")


def create_categories_and_products():
    """Créer des catégories et des produits"""
    print("📦 Création des catégories et produits...")
    
    # Créer des catégories
    categories_data = [
        {'name': 'Smartphones', 'description': 'Téléphones intelligents'},
        {'name': 'Ordinateurs', 'description': 'Ordinateurs portables et de bureau'},
        {'name': 'Accessoires', 'description': 'Accessoires informatiques'},
        {'name': 'Tablettes', 'description': 'Tablettes tactiles'},
        {'name': 'Audio', 'description': 'Écouteurs et enceintes'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories[cat_data['name']] = category
        if created:
            print(f"✅ Catégorie '{cat_data['name']}' créée")
    
    # Créer des produits
    products_data = [
        # Smartphones
        {'name': 'iPhone 15', 'category': 'Smartphones', 'price': 999.00, 'cost_price': 600.00, 'stock': 25},
        {'name': 'Samsung Galaxy S24', 'category': 'Smartphones', 'price': 899.00, 'cost_price': 550.00, 'stock': 18},
        {'name': 'Google Pixel 8', 'category': 'Smartphones', 'price': 699.00, 'cost_price': 400.00, 'stock': 12},
        {'name': 'OnePlus 12', 'category': 'Smartphones', 'price': 799.00, 'cost_price': 450.00, 'stock': 8},
        
        # Ordinateurs
        {'name': 'MacBook Pro 14"', 'category': 'Ordinateurs', 'price': 1999.00, 'cost_price': 1200.00, 'stock': 15},
        {'name': 'Dell XPS 13', 'category': 'Ordinateurs', 'price': 1299.00, 'cost_price': 800.00, 'stock': 10},
        {'name': 'Surface Laptop 5', 'category': 'Ordinateurs', 'price': 1199.00, 'cost_price': 750.00, 'stock': 7},
        {'name': 'HP Spectre x360', 'category': 'Ordinateurs', 'price': 1099.00, 'cost_price': 700.00, 'stock': 5},
        
        # Tablettes
        {'name': 'iPad Air', 'category': 'Tablettes', 'price': 599.00, 'cost_price': 350.00, 'stock': 20},
        {'name': 'Samsung Galaxy Tab S9', 'category': 'Tablettes', 'price': 799.00, 'cost_price': 450.00, 'stock': 12},
        {'name': 'Microsoft Surface Pro 9', 'category': 'Tablettes', 'price': 999.00, 'cost_price': 600.00, 'stock': 8},
        
        # Accessoires
        {'name': 'AirPods Pro', 'category': 'Audio', 'price': 249.00, 'cost_price': 150.00, 'stock': 30},
        {'name': 'Sony WH-1000XM5', 'category': 'Audio', 'price': 399.00, 'cost_price': 250.00, 'stock': 15},
        {'name': 'Apple Watch Series 9', 'category': 'Accessoires', 'price': 399.00, 'cost_price': 250.00, 'stock': 22},
        {'name': 'Magic Mouse', 'category': 'Accessoires', 'price': 79.00, 'cost_price': 40.00, 'stock': 50},
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'category': categories[product_data['category']],
                'description': f"Description du produit {product_data['name']}",
                'price': Decimal(str(product_data['price'])),
                'cost_price': Decimal(str(product_data['cost_price'])),
                'sku': f"SKU-{product_data['name'].replace(' ', '-').upper()}",
                'status': 'active'
            }
        )
        if created:
            print(f"✅ Produit '{product_data['name']}' créé")
            
            # Créer une variante par défaut pour le stock
            ProductVariant.objects.create(
                product=product,
                name='Standard',
                sku=f"{product.sku}-STD",
                variant_type='other',
                value='Standard',
                stock_quantity=product_data['stock'],
                min_stock_level=5,
                max_stock_level=100,
                is_active=True
            )
    
    # Créer des variantes pour certains produits
    products_with_variants = [
        ('iPhone 15', ['128GB', '256GB', '512GB']),
        ('MacBook Pro 14"', ['8GB RAM', '16GB RAM', '32GB RAM']),
        ('iPad Air', ['64GB', '256GB']),
    ]
    
    for product_name, variants in products_with_variants:
        try:
            product = Product.objects.get(name=product_name)
            # Supprimer la variante par défaut
            ProductVariant.objects.filter(product=product, name='Standard').delete()
            
            for i, variant_name in enumerate(variants):
                ProductVariant.objects.create(
                    product=product,
                    name=variant_name,
                    sku=f"{product.sku}-{variant_name.replace(' ', '-')}",
                    variant_type='other',
                    value=variant_name,
                    price_modifier=Decimal(str(i * 100)),  # Prix différent selon la variante
                    stock_quantity=random.randint(5, 20),
                    min_stock_level=3,
                    max_stock_level=50,
                    is_active=True,
                    sort_order=i
                )
            print(f"✅ Variantes créées pour '{product_name}'")
        except Product.DoesNotExist:
            pass


def create_stock_movements():
    """Créer des mouvements de stock"""
    print("📦 Création des mouvements de stock...")
    
    variants = ProductVariant.objects.all()
    users = User.objects.all()
    
    # Mouvements d'entrée (réception de stock)
    for i in range(50):
        variant = random.choice(variants)
        user = random.choice(users)
        quantity = random.randint(1, 20)
        unit_cost = variant.product.cost_price + Decimal(random.uniform(-50, 50))
        
        movement = StockMovement.objects.create(
            product=variant.product,
            variant=variant,
            movement_type='in',
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=quantity * unit_cost,
            reference=f"REC-{i+1:04d}",
            notes=f"Réception de stock - {variant.product.name} {variant.name}",
            user=user,
            is_approved=True,
            approved_by=user
        )
        
        # Mettre à jour le stock de la variante
        variant.stock_quantity += quantity
        variant.save()
    
    # Mouvements de sortie (ventes)
    for i in range(30):
        variant = random.choice(variants)
        user = random.choice(users)
        
        # Vérifier qu'il y a du stock disponible
        if variant.stock_quantity > 0:
            quantity = random.randint(1, min(5, variant.stock_quantity))
            
            movement = StockMovement.objects.create(
                product=variant.product,
                variant=variant,
                movement_type='out',
                quantity=quantity,
                unit_cost=variant.product.cost_price,
                total_cost=quantity * variant.product.cost_price,
                reference=f"VEN-{i+1:04d}",
                notes=f"Vente - {variant.product.name} {variant.name}",
                user=user,
                is_approved=True,
                approved_by=user
            )
            
            # Mettre à jour le stock de la variante
            variant.stock_quantity -= quantity
            variant.save()
    
    print("✅ Mouvements de stock créés")


def create_stock_alerts():
    """Créer des alertes de stock"""
    print("🚨 Création des alertes de stock...")
    
    variants = ProductVariant.objects.all()
    
    for variant in variants:
        # Alerte stock bas si stock < niveau minimum
        if variant.stock_quantity <= variant.min_stock_level and variant.stock_quantity > 0:
            StockAlert.objects.get_or_create(
                product=variant.product,
                variant=variant,
                alert_type='low_stock',
                defaults={
                    'current_quantity': variant.stock_quantity,
                    'threshold_quantity': variant.min_stock_level,
                    'is_active': True
                }
            )
        
        # Alerte rupture de stock si stock = 0
        elif variant.stock_quantity == 0:
            StockAlert.objects.get_or_create(
                product=variant.product,
                variant=variant,
                alert_type='out_of_stock',
                defaults={
                    'current_quantity': 0,
                    'threshold_quantity': variant.min_stock_level,
                    'is_active': True
                }
            )
    
    print("✅ Alertes de stock créées")


def create_orders():
    """Créer des commandes"""
    print("🛒 Création des commandes...")
    
    customers = Customer.objects.all()
    variants = ProductVariant.objects.all()
    users = User.objects.all()
    
    statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
    status_weights = [0.15, 0.25, 0.20, 0.35, 0.05]  # Probabilités
    
    for i in range(100):
        customer = random.choice(customers)
        user = random.choice(users)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Date aléatoire dans les 6 derniers mois
        days_ago = random.randint(1, 180)
        order_date = timezone.now() - timedelta(days=days_ago)
        
        order = Order.objects.create(
            customer=customer,
            user=user,
            order_number=f"CMD-2024-{i+1:03d}",
            order_date=order_date,
            status=status,
            notes=f"Commande test #{i+1}",
            subtotal=Decimal('0.00'),
            tax_amount=Decimal('0.00'),
            total_amount=Decimal('0.00')
        )
        
        # Ajouter des articles à la commande
        num_items = random.randint(1, 5)
        order_items = random.sample(list(variants), min(num_items, len(variants)))
        
        subtotal = Decimal('0.00')
        for variant in order_items:
            quantity = random.randint(1, 3)
            unit_price = variant.final_price
            total_price = quantity * unit_price
            
            OrderItem.objects.create(
                order=order,
                product=variant.product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            
            subtotal += total_price
        
        # Calculer les totaux
        tax_rate = Decimal('0.20')  # 20% de TVA
        tax_amount = subtotal * tax_rate
        total_amount = subtotal + tax_amount
        
        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.total_amount = total_amount
        order.save()
    
    print("✅ Commandes créées")


def create_invoices():
    """Créer des factures"""
    print("💰 Création des factures...")
    
    # Récupérer les commandes confirmées, expédiées ou livrées
    orders = Order.objects.filter(status__in=['confirmed', 'shipped', 'delivered'])
    users = User.objects.all()
    
    statuses = ['paid', 'pending', 'overdue']
    status_weights = [0.60, 0.30, 0.10]  # Probabilités
    
    for i, order in enumerate(orders):
        user = random.choice(users)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Date d'échéance
        due_date = order.order_date + timedelta(days=30)
        
        # Si facture en retard, mettre une date passée
        if status == 'overdue':
            due_date = order.order_date + timedelta(days=random.randint(1, 15))
        
        invoice = Invoice.objects.create(
            order=order,
            user=user,
            invoice_number=f"FAC-2024-{i+1:03d}",
            invoice_date=order.order_date,
            due_date=due_date,
            status=status,
            subtotal=order.subtotal,
            tax_rate=order.tax_rate,
            tax_amount=order.tax_amount,
            total_amount=order.total_amount,
            remaining_amount=order.total_amount if status != 'paid' else Decimal('0.00'),
            notes=f"Facture pour commande {order.order_number}"
        )
        
        # Créer un paiement si la facture est payée
        if status == 'paid':
            Payment.objects.create(
                invoice=invoice,
                user=user,
                amount=invoice.total_amount,
                payment_date=invoice.invoice_date + timedelta(days=random.randint(1, 10)),
                payment_method='bank_transfer',
                reference=f"PAY-{i+1:03d}",
                notes="Paiement test"
            )
    
    print("✅ Factures créées")


def main():
    """Fonction principale"""
    print("🚀 Début du remplissage de la base de données Baobab ERP")
    print("=" * 60)
    
    try:
        # Créer les données dans l'ordre
        create_users_and_roles()
        create_customers()
        create_categories_and_products()
        create_stock_movements()
        create_stock_alerts()
        create_orders()
        create_invoices()
        
        print("\n" + "=" * 60)
        print("🎉 Remplissage terminé avec succès !")
        print("=" * 60)
        
        # Afficher quelques statistiques
        print(f"\n📊 Statistiques générées :")
        print(f"👥 Utilisateurs : {User.objects.count()}")
        print(f"👤 Clients : {Customer.objects.count()}")
        print(f"📦 Produits : {Product.objects.count()}")
        print(f"📋 Commandes : {Order.objects.count()}")
        print(f"💰 Factures : {Invoice.objects.count()}")
        print(f"📦 Mouvements de stock : {StockMovement.objects.count()}")
        print(f"🚨 Alertes : {StockAlert.objects.count()}")
        
        print(f"\n🔑 Comptes de test créés :")
        print(f"   admin / admin123 (Super Admin)")
        print(f"   manager / password123 (Manager)")
        print(f"   sales1 / password123 (Sales)")
        print(f"   stock1 / password123 (Stock Manager)")
        print(f"   viewer / password123 (Viewer)")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du remplissage : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
