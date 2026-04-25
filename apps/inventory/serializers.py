from rest_framework import serializers
from .models import Category, Product, ProductVariant, ProductImage
from apps.common.enums import ProductStatus, ProductType, VariantType


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Category
    """
    full_name = serializers.ReadOnlyField()
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'description',
            'parent',
            'image',
            'is_active',
            'sort_order',
            'full_name',
            'children_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_children_count(self, obj):
        """Retourne le nombre de catégories enfants"""
        return obj.category_set.count()


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des catégories
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id',
            'name',
            'parent',
            'is_active',
            'sort_order',
            'full_name',
            'created_at'
        ]


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle ProductImage
    """
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'alt_text',
            'is_primary',
            'sort_order',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle ProductVariant
    """
    final_price = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id',
            'name',
            'sku',
            'variant_type',
            'value',
            'price_modifier',
            'final_price',
            'stock_quantity',
            'min_stock_level',
            'max_stock_level',
            'is_active',
            'sort_order',
            'is_low_stock',
            'is_out_of_stock',
            'images',
            'primary_image',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_primary_image(self, obj):
        """Retourne l'image principale du variant"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            # Construire l'URL absolue
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(primary_image.image.url)
            else:
                # Fallback si pas de request (tests, etc.)
                image_url = primary_image.image.url
            return {
                'id': primary_image.id,
                'image': image_url,
                'alt_text': primary_image.alt_text
            }
        return None


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Product
    """
    tag_list = serializers.ReadOnlyField()
    total_stock = serializers.SerializerMethodField()
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    primary_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'short_description',
            'sku',
            'barcode',
            'category',
            'category_name',
            'product_type',
            'status',
            'price',
            'cost_price',
            'weight',
            'dimensions',
            'is_digital',
            'is_featured',
            'tags',
            'tag_list',
            'meta_title',
            'meta_description',
            'total_stock',
            'variants',
            'images',
            'primary_image',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_stock(self, obj):
        """Retourne la quantité totale en stock"""
        return obj.get_stock_quantity()

    def get_primary_image(self, obj):
        """Retourne l'image principale du produit"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            # Construire l'URL absolue
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(primary_image.image.url)
            else:
                # Fallback si pas de request (tests, etc.)
                image_url = primary_image.image.url
            return {
                'id': primary_image.id,
                'image': image_url,
                'alt_text': primary_image.alt_text
            }
        return None

    def validate_sku(self, value):
        """Validation du SKU"""
        if Product.objects.filter(sku=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Un produit avec ce SKU existe déjà.")
        return value

    def validate_barcode(self, value):
        """Validation du code-barres"""
        if value and Product.objects.filter(barcode=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Un produit avec ce code-barres existe déjà.")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des produits - Affiche chaque variant comme un produit séparé
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_variant = serializers.SerializerMethodField()
    parent_product_id = serializers.SerializerMethodField()
    parent_product_name = serializers.SerializerMethodField()
    variant_attributes = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'sku',
            'category',
            'category_name',
            'product_type',
            'status',
            'price',
            'is_featured',
            'total_stock',
            'primary_image',
            'is_variant',
            'parent_product_id',
            'parent_product_name',
            'variant_attributes',
            'created_at'
        ]

    def get_total_stock(self, obj):
        """Retourne la quantité totale en stock"""
        if hasattr(obj, 'stock_quantity'):
            # Si c'est un variant, retourner directement stock_quantity
            return obj.stock_quantity
        else:
            # Si c'est un produit, calculer la somme des variants
            return obj.get_stock_quantity()

    def get_primary_image(self, obj):
        """Retourne l'image principale du produit"""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            # Construire l'URL absolue
            request = self.context.get('request')
            if request:
                image_url = request.build_absolute_uri(primary_image.image.url)
            else:
                # Fallback si pas de request (tests, etc.)
                image_url = primary_image.image.url
            return {
                'id': primary_image.id,
                'image': image_url,
                'alt_text': primary_image.alt_text
            }
        return None

    def get_is_variant(self, obj):
        """Indique si c'est un variant d'un produit parent"""
        return hasattr(obj, 'parent_product') and obj.parent_product is not None

    def get_parent_product_id(self, obj):
        """ID du produit parent si c'est un variant"""
        if hasattr(obj, 'parent_product') and obj.parent_product:
            return obj.parent_product.id
        return None

    def get_parent_product_name(self, obj):
        """Nom du produit parent si c'est un variant"""
        if hasattr(obj, 'parent_product') and obj.parent_product:
            return obj.parent_product.name
        return None

    def get_variant_attributes(self, obj):
        """Attributs de variation (couleur, taille, etc.)"""
        if hasattr(obj, 'parent_product') and obj.parent_product:
            return {
                'variant_type': getattr(obj, 'variant_type', None),
                'value': getattr(obj, 'value', None),
                'price_modifier': str(getattr(obj, 'price_modifier', 0)),
                'final_price': float(obj.price + getattr(obj, 'price_modifier', 0))
            }
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de produits
    """
    images = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        write_only=True,
        help_text="Liste des images à associer au produit"
    )
    
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'short_description',
            'sku',
            'barcode',
            'category',
            'product_type',
            'status',
            'price',
            'cost_price',
            'weight',
            'dimensions',
            'is_digital',
            'is_featured',
            'tags',
            'meta_title',
            'meta_description',
            'images'
        ]

    def validate_sku(self, value):
        """Validation du SKU lors de la création"""
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Un produit avec ce SKU existe déjà.")
        return value

    def validate_barcode(self, value):
        """Validation du code-barres lors de la création"""
        if value and Product.objects.filter(barcode=value).exists():
            raise serializers.ValidationError("Un produit avec ce code-barres existe déjà.")
        return value

    def create(self, validated_data):
        """Création du produit avec ses images"""
        request = self.context.get('request')
        
        # Récupérer l'entreprise de l'utilisateur
        if request and hasattr(request, 'user'):
            try:
                user_company = request.user.userprofile.company
            except:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': 'Profil utilisateur non trouvé',
                    'detail': 'Vous devez être associé à une entreprise pour créer des produits'
                })
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Contexte de requête manquant',
                'detail': 'Impossible de déterminer l\'entreprise de l\'utilisateur'
            })
        
        # Extraire les images
        images_data = validated_data.pop('images', [])
        
        # Créer le produit
        validated_data['company'] = user_company
        product = Product.objects.create(**validated_data)
        
        # Créer les images
        for i, image_data in enumerate(images_data):
            image_data['product'] = product
            image_data['company'] = user_company
            image_data.setdefault('is_primary', i == 0)  # Première image = principale
            image_data.setdefault('sort_order', i)
            
            # Convertir les strings en booleans si nécessaire
            if 'is_primary' in image_data and isinstance(image_data['is_primary'], str):
                image_data['is_primary'] = image_data['is_primary'].lower() == 'true'
            
            ProductImage.objects.create(**image_data)
        
        return product


class ProductImageUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des images de produits
    """
    class Meta:
        model = ProductImage
        fields = [
            'id',
            'image',
            'alt_text',
            'is_primary',
            'sort_order'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        """Validation personnalisée pour les images"""
        # Vérifier qu'il n'y a qu'une seule image principale
        if data.get('is_primary', False):
            product = self.context.get('product')
            if product:
                existing_primary = ProductImage.objects.filter(
                    product=product,
                    is_primary=True
                ).exclude(id=self.instance.id if self.instance else None)
                if existing_primary.exists():
                    raise serializers.ValidationError({
                        'is_primary': 'Il ne peut y avoir qu\'une seule image principale par produit.'
                    })
        return data


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour des produits avec gestion des images
    """
    images = ProductImageUpdateSerializer(many=True, required=False)
    images_to_delete = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
        help_text="Liste des IDs des images à supprimer"
    )
    
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'short_description',
            'sku',
            'barcode',
            'category',
            'product_type',
            'status',
            'price',
            'cost_price',
            'weight',
            'dimensions',
            'is_digital',
            'is_featured',
            'tags',
            'meta_title',
            'meta_description',
            'images',
            'images_to_delete'
        ]

    def validate_sku(self, value):
        """Validation du SKU lors de la mise à jour"""
        if Product.objects.filter(sku=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Un produit avec ce SKU existe déjà.")
        return value

    def validate_barcode(self, value):
        """Validation du code-barres lors de la mise à jour"""
        if value and Product.objects.filter(barcode=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Un produit avec ce code-barres existe déjà.")
        return value

    def update(self, instance, validated_data):
        """Mise à jour du produit avec gestion des images"""
        images_data = validated_data.pop('images', [])
        images_to_delete = validated_data.pop('images_to_delete', [])
        
        # Supprimer les images marquées pour suppression
        if images_to_delete:
            ProductImage.objects.filter(
                id__in=images_to_delete,
                product=instance
            ).delete()
        
        # Mettre à jour les données du produit
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Gérer les images
        if images_data:
            # Créer un dictionnaire des images existantes par ID
            existing_images = {img.id: img for img in instance.images.all()}
            
            for image_data in images_data:
                image_id = image_data.get('id')
                if image_id and image_id in existing_images:
                    # Mettre à jour une image existante
                    image = existing_images[image_id]
                    for attr, value in image_data.items():
                        if attr != 'id':
                            setattr(image, attr, value)
                    image.save()
                else:
                    # Créer une nouvelle image
                    ProductImage.objects.create(
                        product=instance,
                        company=instance.company,
                        **image_data
                    )
        
        return instance


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de variants
    """
    class Meta:
        model = ProductVariant
        fields = [
            'product',
            'name',
            'sku',
            'variant_type',
            'value',
            'price_modifier',
            'stock_quantity',
            'min_stock_level',
            'max_stock_level',
            'is_active',
            'sort_order'
        ]

    def validate_sku(self, value):
        """Validation du SKU de la variante"""
        if ProductVariant.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Une variante avec ce SKU existe déjà.")
        return value

    def validate(self, data):
        """Validation croisée"""
        product = data.get('product')
        variant_type = data.get('variant_type')
        value = data.get('value')
        
        if product and variant_type and value:
            if ProductVariant.objects.filter(
                product=product,
                variant_type=variant_type,
                value=value
            ).exists():
                raise serializers.ValidationError(
                    f"Une variante {variant_type}='{value}' existe déjà pour ce produit."
                )
        
        return data

    def create(self, validated_data):
        """Création avec assignation automatique de l'entreprise"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                user_company = request.user.userprofile.company
                validated_data['company'] = user_company
            except:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': 'Profil utilisateur non trouvé',
                    'detail': 'Vous devez être associé à une entreprise pour créer des variants'
                })
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Contexte de requête manquant',
                'detail': 'Impossible de déterminer l\'entreprise de l\'utilisateur'
            })
        
        return super().create(validated_data)


class ProductWithVariantsCreateSerializer(serializers.Serializer):
    """
    Serializer pour créer un produit avec ses variants en une seule requête
    """
    # Champs du produit
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True, max_length=None)
    short_description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    sku = serializers.CharField(max_length=100)
    barcode = serializers.CharField(max_length=100, required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    product_type = serializers.ChoiceField(choices=ProductType.choices, default=ProductType.SIMPLE)
    status = serializers.ChoiceField(choices=ProductStatus.choices, default=ProductStatus.ACTIVE)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    cost_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    weight = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    dimensions = serializers.CharField(max_length=100, required=False, allow_blank=True)
    is_digital = serializers.BooleanField(default=False)
    is_featured = serializers.BooleanField(default=False)
    tags = serializers.CharField(max_length=500, required=False, allow_blank=True)
    meta_title = serializers.CharField(max_length=200, required=False, allow_blank=True)
    meta_description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    # Liste des variants
    variants = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        help_text="Liste des variants du produit"
    )
    
    # Images du produit
    images = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True,
        help_text="Liste des images du produit"
    )

    def validate_sku(self, value):
        """Validation du SKU du produit"""
        if Product.objects.filter(sku=value).exists():
            raise serializers.ValidationError("Un produit avec ce SKU existe déjà.")
        return value

    def validate_barcode(self, value):
        """Validation du code-barres"""
        if value and Product.objects.filter(barcode=value).exists():
            raise serializers.ValidationError("Un produit avec ce code-barres existe déjà.")
        return value

    def validate_variants(self, value):
        """Validation des variants"""
        if not value:
            return value
            
        # Vérifier que chaque variant a les champs requis
        required_fields = ['name', 'sku', 'variant_type', 'value']
        for i, variant in enumerate(value):
            for field in required_fields:
                if field not in variant:
                    raise serializers.ValidationError(
                        f"Le variant {i+1} doit avoir le champ '{field}'"
                    )
            
            # Vérifier l'unicité du SKU des variants
            if ProductVariant.objects.filter(sku=variant['sku']).exists():
                raise serializers.ValidationError(
                    f"Une variante avec le SKU '{variant['sku']}' existe déjà."
                )
        
        return value

    def _parse_multipart_variants(self, request):
        """Parser les variants depuis les données multipart"""
        variants_data = []
        
        # Compter le nombre de variants
        variant_count = 0
        for key in request.data.keys():
            if key.startswith('variants[') and '].name' in key:
                variant_count += 1
        
        # Parser chaque variant
        for i in range(variant_count):
            variant_data = {}
            variant_images = []
            
            # Parser les champs du variant
            for key, value in request.data.items():
                if key.startswith(f'variants[{i}].'):
                    field_name = key.replace(f'variants[{i}].', '')
                    
                    if field_name.startswith('images['):
                        # C'est une image du variant
                        image_index = int(field_name.split('[')[1].split(']')[0])
                        image_field = field_name.split('.')[-1]
                        
                        # Initialiser l'image si elle n'existe pas
                        while len(variant_images) <= image_index:
                            variant_images.append({})
                        
                        if image_field == 'image':
                            variant_images[image_index]['image'] = value
                        elif image_field == 'alt_text':
                            variant_images[image_index]['alt_text'] = value
                        elif image_field == 'is_primary':
                            variant_images[image_index]['is_primary'] = value
                        elif image_field == 'sort_order':
                            variant_images[image_index]['sort_order'] = int(value) if value else 0
                    else:
                        # C'est un champ normal du variant
                        variant_data[field_name] = value
            
            # Ajouter les images au variant
            if variant_images:
                variant_data['images'] = variant_images
            
            # Nettoyer les données du variant (enlever les champs qui ne sont pas du modèle)
            clean_variant_data = {
                'name': variant_data.get('name'),
                'sku': variant_data.get('sku'),
                'variant_type': variant_data.get('variant_type'),
                'value': variant_data.get('value'),
                'price_modifier': variant_data.get('price_modifier', 0.00),
                'stock_quantity': variant_data.get('stock_quantity', 0),
                'min_stock_level': variant_data.get('min_stock_level', 0),
                'max_stock_level': variant_data.get('max_stock_level', 1000),
                'is_active': variant_data.get('is_active', True),
                'sort_order': variant_data.get('sort_order', 1)
            }
            
            # Convertir les strings en booleans si nécessaire
            if 'is_active' in variant_data and isinstance(variant_data['is_active'], str):
                clean_variant_data['is_active'] = variant_data['is_active'].lower() == 'true'
            
            if clean_variant_data.get('name'):  # Seulement ajouter si le variant a un nom
                variants_data.append(clean_variant_data)
        
        return variants_data

    def _parse_multipart_images(self, request, prefix):
        """Parser les images depuis les données multipart"""
        images_data = []
        
        # Compter le nombre d'images
        image_count = 0
        for key in request.data.keys():
            if key.startswith(f'{prefix}[') and f'].{prefix.split(".")[-1] if "." in prefix else "image"}' in key:
                image_count += 1
        
        # Parser chaque image
        for i in range(image_count):
            image_data = {}
            
            for key, value in request.data.items():
                if key.startswith(f'{prefix}[{i}].'):
                    field_name = key.replace(f'{prefix}[{i}].', '')
                    image_data[field_name] = value
            
            if image_data:  # Seulement ajouter si l'image a des données
                images_data.append(image_data)
        
        return images_data

    def create(self, validated_data):
        """Création du produit avec ses variants"""
        request = self.context.get('request')
        
        # Récupérer l'entreprise de l'utilisateur
        if request and hasattr(request, 'user'):
            try:
                user_company = request.user.userprofile.company
            except:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': 'Profil utilisateur non trouvé',
                    'detail': 'Vous devez être associé à une entreprise pour créer des produits'
                })
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Contexte de requête manquant',
                'detail': 'Impossible de déterminer l\'entreprise de l\'utilisateur'
            })
        
        # Parser les données multipart pour les variants et images
        variants_data = self._parse_multipart_variants(request)
        images_data = self._parse_multipart_images(request, 'images')
        
        # Supprimer les champs variants et images des validated_data s'ils existent
        validated_data.pop('variants', None)
        validated_data.pop('images', None)
        
        # Créer le produit
        validated_data['company'] = user_company
        product = Product.objects.create(**validated_data)
        
        # Créer les images du produit
        for i, image_data in enumerate(images_data):
            image_data['product'] = product
            image_data['company'] = user_company
            image_data.setdefault('is_primary', i == 0)  # Première image = principale
            image_data.setdefault('sort_order', i)
            
            # Convertir les strings en booleans si nécessaire
            if 'is_primary' in image_data and isinstance(image_data['is_primary'], str):
                image_data['is_primary'] = image_data['is_primary'].lower() == 'true'
            
            ProductImage.objects.create(**image_data)
        
        # Créer les variants
        created_variants = []
        for variant_data in variants_data:
            # Extraire les images du variant (optionnelles)
            variant_images = variant_data.pop('images', [])
            
            # Créer le variant
            variant = ProductVariant.objects.create(
                product=product,
                company=user_company,
                name=variant_data.get('name'),
                sku=variant_data.get('sku'),
                variant_type=variant_data.get('variant_type'),
                value=variant_data.get('value'),
                price_modifier=variant_data.get('price_modifier', 0.00),
                stock_quantity=variant_data.get('stock_quantity', 0),
                min_stock_level=variant_data.get('min_stock_level', 0),
                max_stock_level=variant_data.get('max_stock_level', 1000),
                is_active=variant_data.get('is_active', True),
                sort_order=len(created_variants) + 1
            )
            
            # Créer les images du variant (si fournies)
            for i, image_data in enumerate(variant_images):
                image_data['variant'] = variant
                image_data['company'] = user_company
                image_data.setdefault('is_primary', i == 0)  # Première image = principale
                image_data.setdefault('sort_order', i)
                
                # Convertir les strings en booleans si nécessaire
                if 'is_primary' in image_data and isinstance(image_data['is_primary'], str):
                    image_data['is_primary'] = image_data['is_primary'].lower() == 'true'
                
                ProductImage.objects.create(**image_data)
            
            created_variants.append(variant)
        
        # Ajouter les variants créés au produit pour la réponse
        product.variants_created = created_variants
        return product
