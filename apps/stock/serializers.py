from rest_framework import serializers
from .models import StockMovement, StockAdjustment, StockAlert, StockReport
from apps.inventory.serializers import ProductSerializer, ProductVariantSerializer
from apps.common.serializers import UserSerializer


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer pour les mouvements de stock
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    is_entry = serializers.ReadOnlyField()
    is_exit = serializers.ReadOnlyField()
    absolute_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'variant', 'variant_name',
            'movement_type', 'quantity', 'unit_cost', 'total_cost',
            'reference', 'notes', 'user', 'user_name', 'is_approved',
            'approved_by', 'approved_by_name', 'approved_at',
            'is_entry', 'is_exit', 'absolute_quantity',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_cost']

    def validate_quantity(self, value):
        """Validation de la quantité"""
        if value == 0:
            raise serializers.ValidationError("La quantité ne peut pas être zéro.")
        return value

    def validate(self, data):
        """Validation globale"""
        # Vérifier que le produit et la variante sont cohérents
        if data.get('variant') and data.get('product'):
            if data['variant'].product != data['product']:
                raise serializers.ValidationError(
                    "La variante doit appartenir au produit sélectionné."
                )
        return data


class StockMovementCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de mouvements de stock
    """
    class Meta:
        model = StockMovement
        fields = [
            'product', 'variant', 'movement_type', 'quantity',
            'unit_cost', 'reference', 'notes'
        ]

    def validate_quantity(self, value):
        """Validation de la quantité"""
        if value == 0:
            raise serializers.ValidationError("La quantité ne peut pas être zéro.")
        return value

    def create(self, validated_data):
        """Créer un mouvement de stock"""
        # Ajouter l'utilisateur actuel
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StockAdjustmentSerializer(serializers.ModelSerializer):
    """
    Serializer pour les ajustements de stock
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'product', 'product_name', 'variant', 'variant_name',
            'adjustment_type', 'quantity_before', 'quantity_after',
            'adjustment_quantity', 'reason', 'user', 'user_name',
            'is_approved', 'approved_by', 'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'adjustment_quantity']

    def validate_quantity_after(self, value):
        """Validation de la quantité après"""
        if value < 0:
            raise serializers.ValidationError("La quantité après ne peut pas être négative.")
        return value

    def validate(self, data):
        """Validation globale"""
        # Vérifier que le produit et la variante sont cohérents
        if data.get('variant') and data.get('product'):
            if data['variant'].product != data['product']:
                raise serializers.ValidationError(
                    "La variante doit appartenir au produit sélectionné."
                )
        return data


class StockAdjustmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'ajustements de stock
    """
    class Meta:
        model = StockAdjustment
        fields = [
            'product', 'variant', 'adjustment_type', 'quantity_before',
            'quantity_after', 'reason'
        ]

    def validate_quantity_after(self, value):
        """Validation de la quantité après"""
        if value < 0:
            raise serializers.ValidationError("La quantité après ne peut pas être négative.")
        return value

    def create(self, validated_data):
        """Créer un ajustement de stock"""
        # Ajouter l'utilisateur actuel
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StockAlertSerializer(serializers.ModelSerializer):
    """
    Serializer pour les alertes de stock
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    is_overstock = serializers.ReadOnlyField()
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product', 'product_name', 'variant', 'variant_name',
            'alert_type', 'current_quantity', 'threshold_quantity',
            'is_active', 'is_resolved', 'resolved_at', 'resolved_by',
            'resolved_by_name', 'is_low_stock', 'is_out_of_stock',
            'is_overstock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_current_quantity(self, value):
        """Validation de la quantité actuelle"""
        if value < 0:
            raise serializers.ValidationError("La quantité actuelle ne peut pas être négative.")
        return value

    def validate_threshold_quantity(self, value):
        """Validation de la quantité seuil"""
        if value < 0:
            raise serializers.ValidationError("La quantité seuil ne peut pas être négative.")
        return value


class StockReportSerializer(serializers.ModelSerializer):
    """
    Serializer pour les rapports de stock
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    period_days = serializers.ReadOnlyField()
    
    class Meta:
        model = StockReport
        fields = [
            'id', 'report_type', 'title', 'description', 'date_from',
            'date_to', 'filters', 'data', 'user', 'user_name',
            'is_generated', 'generated_at', 'period_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'period_days']

    def validate_date_to(self, value):
        """Validation de la date de fin"""
        if hasattr(self, 'initial_data') and 'date_from' in self.initial_data:
            date_from = self.initial_data['date_from']
            if value < date_from:
                raise serializers.ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )
        return value

    def create(self, validated_data):
        """Créer un rapport de stock"""
        # Ajouter l'utilisateur actuel
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StockMovementListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des mouvements
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_entry = serializers.ReadOnlyField()
    is_exit = serializers.ReadOnlyField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product_name', 'variant_name', 'movement_type',
            'quantity', 'unit_cost', 'total_cost', 'reference',
            'user_name', 'is_approved', 'is_entry', 'is_exit',
            'created_at'
        ]


class StockAdjustmentListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des ajustements
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'product_name', 'variant_name', 'adjustment_type',
            'quantity_before', 'quantity_after', 'adjustment_quantity',
            'user_name', 'is_approved', 'created_at'
        ]


class StockAlertListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des alertes
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_name = serializers.CharField(source='variant.name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    is_overstock = serializers.ReadOnlyField()
    
    class Meta:
        model = StockAlert
        fields = [
            'id', 'product_name', 'variant_name', 'alert_type',
            'current_quantity', 'threshold_quantity', 'is_active',
            'is_resolved', 'is_low_stock', 'is_out_of_stock',
            'is_overstock', 'created_at'
        ]