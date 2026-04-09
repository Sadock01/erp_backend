#!/usr/bin/env python3
"""
Script pour ajouter des images aux produits existants via l'API PATCH
Utilise l'API d'inventaire pour modifier les produits avec des images du dossier products/
"""

import os
import sys
import json
import requests
import base64
from pathlib import Path
from typing import List, Dict, Optional
from requests_toolbelt.multipart.encoder import MultipartEncoder

# Configuration
API_BASE_URL = "http://localhost:8000/api"
ADMIN_TOKEN = "1e367e68c1a81d5ed312eae081c2faba21d40676"
PRODUCTS_IMAGES_DIR = "products"

# Headers pour les requêtes API
HEADERS = {
    "Authorization": f"Token {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

def get_products() -> List[Dict]:
    """Récupérer la liste des produits existants"""
    try:
        response = requests.get(f"{API_BASE_URL}/inventory/products/", headers=HEADERS)
        response.raise_for_status()
        return response.json().get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la récupération des produits: {e}")
        return []

def get_available_images() -> List[str]:
    """Récupérer la liste des images disponibles dans le dossier products/"""
    images_dir = Path(PRODUCTS_IMAGES_DIR)
    if not images_dir.exists():
        print(f"❌ Le dossier {PRODUCTS_IMAGES_DIR} n'existe pas")
        return []
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    images = []
    
    for file_path in images_dir.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            images.append(str(file_path))
    
    print(f"📁 {len(images)} images trouvées dans {PRODUCTS_IMAGES_DIR}/")
    return images

def encode_image_to_base64(image_path: str) -> Optional[str]:
    """Encoder une image en base64"""
    try:
        with open(image_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except Exception as e:
        print(f"❌ Erreur lors de l'encodage de {image_path}: {e}")
        return None

def map_image_to_product(product: Dict, available_images: List[str]) -> Optional[str]:
    """Mapper une image appropriée à un produit basé sur son nom/catégorie"""
    product_name = product.get('name', '').lower()
    # La catégorie peut être un ID (int) ou un objet, on gère les deux cas
    category = product.get('category', {})
    if isinstance(category, dict):
        category_name = category.get('name', '').lower()
    else:
        category_name = ''
    
    # Mappings basés sur des mots-clés
    mappings = {
        'phone': ['801864e4-cd12-4a18-b657-422200fca3ba.jpg'],
        'smartphone': ['801864e4-cd12-4a18-b657-422200fca3ba.jpg'],
        'iphone': ['801864e4-cd12-4a18-b657-422200fca3ba.jpg'],
        'samsung': ['801864e4-cd12-4a18-b657-422200fca3ba.jpg'],
        'galaxy': ['801864e4-cd12-4a18-b657-422200fca3ba.jpg'],
        'laptop': ['pexels-mert-coskun-386432351-33506116.jpg'],
        'macbook': ['pexels-mert-coskun-386432351-33506116.jpg'],
        'computer': ['pexels-mert-coskun-386432351-33506116.jpg'],
        'ordinateur': ['pexels-mert-coskun-386432351-33506116.jpg'],
        'shirt': ['sanju-pandita-to6a5Cf1xGE-unsplash.jpg'],
        'chemise': ['sanju-pandita-to6a5Cf1xGE-unsplash.jpg'],
        'vêtement': ['sanju-pandita-to6a5Cf1xGE-unsplash.jpg'],
        'clothing': ['sanju-pandita-to6a5Cf1xGE-unsplash.jpg'],
        'clothes': ['sanju-pandita-to6a5Cf1xGE-unsplash.jpg']
    }
    
    # Chercher une correspondance
    for keyword, image_files in mappings.items():
        if keyword in product_name or keyword in category_name:
            for image_file in image_files:
                image_path = os.path.join(PRODUCTS_IMAGES_DIR, image_file)
                if os.path.exists(image_path):
                    return image_path
    
    # Si aucune correspondance, utiliser la première image disponible
    if available_images:
        return available_images[0]
    
    return None

def update_product_with_image(product_id: int, image_path: str) -> bool:
    """Mettre à jour un produit avec une image via l'API PATCH"""
    try:
        # Lire le fichier image
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        # Déterminer le type MIME
        file_extension = os.path.splitext(image_path)[1].lower()
        mime_type = 'image/jpeg'
        if file_extension in ['.png']:
            mime_type = 'image/png'
        elif file_extension in ['.gif']:
            mime_type = 'image/gif'
        elif file_extension in ['.webp']:
            mime_type = 'image/webp'
        
        # Créer le multipart encoder
        multipart_data = MultipartEncoder(
            fields={
                'images[0][image]': (os.path.basename(image_path), image_data, mime_type),
                'images[0][alt_text]': f'Image du produit {product_id}',
                'images[0][is_primary]': 'true',
                'images[0][sort_order]': '1'
            }
        )
        
        # Headers pour multipart/form-data
        headers = {
            "Authorization": f"Token {ADMIN_TOKEN}",
            "Content-Type": multipart_data.content_type
        }
        
        # Faire la requête PATCH
        response = requests.patch(
            f"{API_BASE_URL}/inventory/products/{product_id}/",
            headers=headers,
            data=multipart_data
        )
        
        if response.status_code == 200:
            print(f"✅ Produit {product_id} mis à jour avec l'image {os.path.basename(image_path)}")
            return True
        else:
            print(f"❌ Erreur lors de la mise à jour du produit {product_id}: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du produit {product_id}: {e}")
        return False

def main():
    """Fonction principale"""
    print("🚀 Début du script d'ajout d'images aux produits")
    print("=" * 50)
    
    # 1. Récupérer les produits existants
    print("📦 Récupération des produits existants...")
    products = get_products()
    if not products:
        print("❌ Aucun produit trouvé")
        return
    
    print(f"✅ {len(products)} produits trouvés")
    
    # 2. Récupérer les images disponibles
    print("\n🖼️  Récupération des images disponibles...")
    available_images = get_available_images()
    if not available_images:
        print("❌ Aucune image trouvée")
        return
    
    # 3. Traiter chaque produit
    print(f"\n🔄 Traitement de {len(products)} produits...")
    success_count = 0
    error_count = 0
    
    for i, product in enumerate(products, 1):
        product_id = product.get('id')
        product_name = product.get('name', 'Sans nom')
        
        print(f"\n[{i}/{len(products)}] Traitement du produit: {product_name} (ID: {product_id})")
        
        # Vérifier si le produit a déjà des images
        existing_images = product.get('images', [])
        if existing_images:
            print(f"   ⚠️  Le produit a déjà {len(existing_images)} image(s), passage au suivant")
            continue
        
        # Mapper une image au produit
        image_path = map_image_to_product(product, available_images)
        if not image_path:
            print(f"   ⚠️  Aucune image appropriée trouvée pour ce produit")
            continue
        
        print(f"   🖼️  Image sélectionnée: {os.path.basename(image_path)}")
        
        # Mettre à jour le produit
        if update_product_with_image(product_id, image_path):
            success_count += 1
        else:
            error_count += 1
    
    # 4. Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ")
    print(f"✅ Produits mis à jour avec succès: {success_count}")
    print(f"❌ Erreurs: {error_count}")
    print(f"📦 Total des produits traités: {len(products)}")
    
    if success_count > 0:
        print(f"\n🎉 {success_count} produits ont été mis à jour avec des images!")
    else:
        print("\n⚠️  Aucun produit n'a été mis à jour")

if __name__ == "__main__":
    main()
