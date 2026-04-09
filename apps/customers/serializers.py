from rest_framework import serializers
from .models import Customer


class CustomerKPIsSerializer(serializers.Serializer):
    """
    Serializer pour les KPIs des clients
    """
    total_clients = serializers.IntegerField()
    total_clients_growth = serializers.DecimalField(max_digits=5, decimal_places=1)
    active_clients = serializers.IntegerField()
    active_clients_percentage = serializers.DecimalField(max_digits=5, decimal_places=1)
    companies = serializers.IntegerField()
    companies_percentage = serializers.DecimalField(max_digits=5, decimal_places=1)
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=0)
    revenue_currency = serializers.CharField()
    revenue_description = serializers.CharField()


class CustomerSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Customer
    """
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'company',
            'address',
            'city',
            'postal_code',
            'country',
            'is_active',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_email(self, value):
        """Validation personnalisée pour l'email"""
        if Customer.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Un client avec cet email existe déjà.")
        return value

    def validate_phone(self, value):
        """Validation personnalisée pour le téléphone"""
        if value and len(value) < 10:
            raise serializers.ValidationError("Le numéro de téléphone doit contenir au moins 10 caractères.")
        return value


class CustomerListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des clients avec données enrichies
    """
    full_name = serializers.ReadOnlyField()
    last_order_date = serializers.SerializerMethodField()
    total_orders = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    customer_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'phone',
            'company',
            'address',
            'city',
            'postal_code',
            'country',
            'is_active',
            'notes',
            'created_at',
            'updated_at',
            'last_order_date',
            'total_orders',
            'total_spent',
            'customer_type'
        ]
    
    def get_last_order_date(self, obj):
        """Récupérer la date de la dernière commande"""
        try:
            from apps.sales.models import Order
            last_order = Order.objects.filter(
                customer=obj,
                status__in=['confirmed', 'shipped', 'delivered']
            ).order_by('-created_at').first()
            return last_order.created_at if last_order else None
        except ImportError:
            return None
    
    def get_total_orders(self, obj):
        """Récupérer le nombre total de commandes"""
        try:
            from apps.sales.models import Order
            return Order.objects.filter(
                customer=obj,
                status__in=['confirmed', 'shipped', 'delivered']
            ).count()
        except ImportError:
            return 0
    
    def get_total_spent(self, obj):
        """Récupérer le montant total dépensé"""
        try:
            from apps.sales.models import Order
            from django.db.models import Sum
            total = Order.objects.filter(
                customer=obj,
                status__in=['confirmed', 'shipped', 'delivered']
            ).aggregate(total=Sum('total_amount'))['total']
            return int(total) if total else 0
        except ImportError:
            return 0
    
    def get_customer_type(self, obj):
        """Déterminer le type de client"""
        # Vérifier si le client a une entreprise (client_company) ou une company associée
        if obj.client_company and obj.client_company.strip():
            return "company"
        return "individual"


class CustomerCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de clients
    """
    class Meta:
        model = Customer
        fields = [
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'client_company',
            'address',
            'city',
            'postal_code',
            'country',
            'notes',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'is_active', 'created_at', 'updated_at']

    def validate_email(self, value):
        """Validation de l'email lors de la création"""
        if Customer.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un client avec cet email existe déjà.")
        return value

    def create(self, validated_data):
        """Créer un client avec le company de l'utilisateur connecté"""
        # Récupérer le company de l'utilisateur connecté
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                user_company = request.user.userprofile.company
                validated_data['company'] = user_company
            except:
                from rest_framework.exceptions import ValidationError
                raise ValidationError({
                    'error': 'Profil utilisateur non trouvé',
                    'detail': 'Vous devez être associé à une entreprise pour créer des clients'
                })
        else:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Contexte de requête manquant',
                'detail': 'Impossible de déterminer l\'entreprise de l\'utilisateur'
            })
        
        return super().create(validated_data)
