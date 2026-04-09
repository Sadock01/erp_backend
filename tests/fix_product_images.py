#!/usr/bin/env python
"""
Script pour corriger les images des produits
"""
import os
import sys
import django
from pathlib import Path

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nodus.settings')
django.setup()

from apps.inventory.models import Product, ProductImage

def fix_product_images():
    """Corriger les images des produits"""
    print("🔧 Correction des images des produits")
    print("=" * 50)
    
    # Dossier des images
    images_dir = Path("products")
    if not images_dir.exists():
        print("❌ Dossier 'products' introuvable")
        return
    
    # Liste des images disponibles
    image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.jpeg")) + list(images_dir.glob("*.png"))
    print(f"📁 {len(image_files)} images trouvées")
    
    if not image_files:
        print("❌ Aucune image trouvée")
        return
    
    # Récupérer tous les produits
    products = Product.objects.all()
    print(f"📦 {products.count()} produits trouvés")
    
    # 1. Marquer les images existantes comme principales
    print("\n1️⃣ Marquer les images existantes comme principales...")
    for product in products:
        existing_images = product.images.all()
        if existing_images.exists():
            # Prendre la première image et la marquer comme principale
            first_image = existing_images.first()
            first_image.is_primary = True
            first_image.alt_text = f"Image de {product.name}"
            first_image.save()
            print(f"   ✅ {product.name}: Image existante marquée comme principale")
    
    # 2. Ajouter des images aux produits qui n'en ont pas
    print("\n2️⃣ Ajouter des images aux produits sans image...")
    products_without_images = products.filter(images__isnull=True)
    print(f"📦 {products_without_images.count()} produits sans image")
    
    for i, product in enumerate(products_without_images, 1):
        # Sélectionner une image au hasard
        image_file = image_files[i % len(image_files)]
        
        print(f"[{i}/{products_without_images.count()}] Ajout d'image pour {product.name}")
        
        # Créer l'image avec le bon format
        from django.core.files import File
        with open(image_file, 'rb') as f:
            django_file = File(f, name=image_file.name)
            product_image = ProductImage.objects.create(
                product=product,
                image=django_file,
                alt_text=f"Image de {product.name}",
                is_primary=True,
                sort_order=1
            )
        
        print(f"   ✅ Image ajoutée: {product_image.image.name}")
    
    print("=" * 50)
    print("🎉 Correction terminée!")
    print(f"✅ {ProductImage.objects.count()} images totales")
    print(f"✅ {ProductImage.objects.filter(is_primary=True).count()} images principales")
    print(f"✅ {products.filter(images__isnull=False).count()}/{products.count()} produits avec images")

if __name__ == "__main__":
    fix_product_images()
