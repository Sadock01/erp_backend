from rest_framework import serializers
from .models import Order, OrderItem, Invoice, ProformaInvoice, Payment
from apps.customers.serializers import CustomerSerializer
from apps.inventory.serializers import ProductSerializer, ProductVariantSerializer
from apps.common.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer pour les articles de commande
    """
    product_name = serializers.ReadOnlyField()
    final_unit_price = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order', 'product', 'variant', 'quantity', 'unit_price',
            'discount_rate', 'discount_amount', 'total_price', 'product_name',
            'final_unit_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'total_price']

    def validate_quantity(self, value):
        """Validation de la quantité"""
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être positive.")
        return value

    def validate_unit_price(self, value):
        """Validation du prix unitaire"""
        if value <= 0:
            raise serializers.ValidationError("Le prix unitaire doit être positif.")
        return value

    def validate(self, data):
        """Validation globale"""
        if data.get('variant') and data.get('product'):
            if data['variant'].product != data['product']:
                raise serializers.ValidationError(
                    "La variante doit appartenir au produit sélectionné."
                )
        return data


class OrderItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'articles de commande
    """
    class Meta:
        model = OrderItem
        fields = [
            'product', 'variant', 'quantity', 'unit_price', 'discount_rate'
        ]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La quantité doit être positive.")
        return value

    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le prix unitaire doit être positif.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer pour les commandes
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    is_pending = serializers.ReadOnlyField()
    is_confirmed = serializers.ReadOnlyField()
    is_shipped = serializers.ReadOnlyField()
    is_delivered = serializers.ReadOnlyField()
    is_cancelled = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'order_number', 'status',
            'order_date', 'delivery_date', 'subtotal', 'tax_rate', 'tax_amount',
            'total_amount', 'discount_rate', 'discount_amount', 'notes',
            'internal_notes', 'user', 'user_name', 'items', 'is_pending',
            'is_confirmed', 'is_shipped', 'is_delivered', 'is_cancelled',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'order_number']

    def validate_discount_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Le taux de remise doit être entre 0 et 100.")
        return value

    def validate_tax_rate(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Le taux de TVA doit être entre 0 et 100.")
        return value


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de commandes
    """
    items = OrderItemCreateSerializer(many=True, write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'customer', 'status', 'order_date', 'delivery_date', 'tax_rate',
            'discount_rate', 'notes', 'internal_notes', 'items'
        ]

    def create(self, validated_data):
        """Créer une commande avec ses articles"""
        items_data = validated_data.pop('items')
        validated_data['user'] = self.context['request'].user
        
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        order.calculate_totals()
        return order

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("La commande doit contenir au moins un article.")
        return value


class OrderListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des commandes
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'order_number', 'status', 'order_date',
            'total_amount', 'user_name', 'items_count', 'created_at'
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les factures
    """
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    customer_name = serializers.CharField(source='order.customer.full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_draft = serializers.ReadOnlyField()
    is_sent = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    is_overdue = serializers.ReadOnlyField()
    payment_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'order', 'order_number', 'customer_name', 'invoice_number',
            'status', 'invoice_date', 'due_date', 'subtotal', 'tax_rate',
            'tax_amount', 'total_amount', 'paid_amount', 'remaining_amount',
            'notes', 'user', 'user_name', 'is_draft', 'is_sent', 'is_paid',
            'is_overdue', 'payment_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'invoice_number']

    def validate_due_date(self, value):
        if hasattr(self, 'initial_data') and 'invoice_date' in self.initial_data:
            invoice_date = self.initial_data['invoice_date']
            if value < invoice_date:
                raise serializers.ValidationError(
                    "La date d'échéance doit être postérieure à la date de facture."
                )
        return value


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de factures
    """
    class Meta:
        model = Invoice
        fields = [
            'order', 'status', 'invoice_date', 'due_date', 'notes'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        invoice = Invoice.objects.create(**validated_data)
        invoice.calculate_totals()
        return invoice


class ProformaInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer pour les devis
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_draft = serializers.ReadOnlyField()
    is_sent = serializers.ReadOnlyField()
    is_accepted = serializers.ReadOnlyField()
    is_rejected = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = ProformaInvoice
        fields = [
            'id', 'customer', 'customer_name', 'proforma_number', 'status',
            'proforma_date', 'valid_until', 'subtotal', 'tax_rate', 'tax_amount',
            'total_amount', 'notes', 'user', 'user_name', 'is_draft', 'is_sent',
            'is_accepted', 'is_rejected', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'proforma_number']

    def validate_valid_until(self, value):
        if hasattr(self, 'initial_data') and 'proforma_date' in self.initial_data:
            proforma_date = self.initial_data['proforma_date']
            if value < proforma_date:
                raise serializers.ValidationError(
                    "La date de validité doit être postérieure à la date du devis."
                )
        return value


class ProformaInvoiceCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de devis
    """
    class Meta:
        model = ProformaInvoice
        fields = [
            'customer', 'status', 'proforma_date', 'valid_until', 'subtotal',
            'tax_rate', 'tax_amount', 'total_amount', 'notes'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return ProformaInvoice.objects.create(**validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    """
    Serializer pour les paiements
    """
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    customer_name = serializers.CharField(source='invoice.order.customer.full_name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice', 'invoice_number', 'customer_name', 'payment_method',
            'amount', 'payment_date', 'reference', 'notes', 'user', 'user_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif.")
        return value


class PaymentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de paiements
    """
    class Meta:
        model = Payment
        fields = [
            'invoice', 'payment_method', 'amount', 'payment_date', 'reference', 'notes'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        payment = Payment.objects.create(**validated_data)
        
        invoice = payment.invoice
        invoice.paid_amount = sum(p.amount for p in invoice.payments.all())
        invoice.calculate_totals()
        
        return payment

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif.")
        return value


class OrderItemListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des articles de commande
    """
    product_name = serializers.ReadOnlyField()
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'order_number', 'product_name', 'quantity', 'unit_price',
            'total_price', 'created_at'
        ]


class InvoiceListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des factures
    """
    customer_name = serializers.CharField(source='order.customer.full_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    payment_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer_name', 'order_number', 'status',
            'invoice_date', 'due_date', 'total_amount', 'paid_amount',
            'remaining_amount', 'is_overdue', 'payment_percentage', 'created_at'
        ]


class ProformaInvoiceListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des devis
    """
    customer_name = serializers.CharField(source='customer.full_name', read_only=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = ProformaInvoice
        fields = [
            'id', 'proforma_number', 'customer_name', 'status', 'proforma_date',
            'valid_until', 'total_amount', 'is_expired', 'created_at'
        ]


class PaymentListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des paiements
    """
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    customer_name = serializers.CharField(source='invoice.order.customer.full_name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'invoice_number', 'customer_name', 'payment_method',
            'amount', 'payment_date', 'reference', 'created_at'
        ]