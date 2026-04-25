# Serializers communs
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Alert, Notification, Company


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle User
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserSelfUpdateSerializer(serializers.ModelSerializer):
    """
    Mise à jour du compte par l'utilisateur connecté (PATCH /api/auth/profile/).
    """

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError('Cet email est déjà utilisé.')
        return value

    def update(self, instance, validated_data):
        if 'email' in validated_data:
            instance.username = validated_data['email']
        return super().update(instance, validated_data)


class CompanyMyUpdateSerializer(serializers.ModelSerializer):
    """
    Mise à jour de l'entreprise courante (PATCH /api/companies/my/).
    Pas de désactivation du tenant via cette route (pas de champ is_active).
    """

    class Meta:
        model = Company
        fields = [
            'name',
            'logo',
            'primary_color',
            'description',
            'email',
            'phone',
            'address',
            'city',
            'postal_code',
            'country',
            'website',
            'tax_number',
            'registration_number',
            'settings',
        ]


class LoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion avec email
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        """Validation de l'email"""
        if not value:
            raise serializers.ValidationError("L'email est requis.")
        return value

    def validate_password(self, value):
        """Validation du mot de passe"""
        if not value:
            raise serializers.ValidationError("Le mot de passe est requis.")
        return value


class RegisterSerializer(serializers.Serializer):
    """
    Serializer pour l'inscription d'un nouvel utilisateur avec création d'entreprise
    """
    # Champs utilisateur
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    
    # Champs entreprise (requis)
    company_name = serializers.CharField(max_length=200, help_text="Nom de l'entreprise")
    company_description = serializers.CharField(required=False, allow_blank=True, help_text="Description de l'entreprise")
    company_phone = serializers.CharField(max_length=20, help_text="Téléphone de l'entreprise")
    company_address = serializers.CharField(required=False, allow_blank=True, help_text="Adresse de l'entreprise")
    company_city = serializers.CharField(max_length=100, help_text="Ville de l'entreprise")
    company_postal_code = serializers.CharField(max_length=10, required=False, allow_blank=True, help_text="Code postal de l'entreprise")
    company_country = serializers.CharField(max_length=100, default="France", help_text="Pays de l'entreprise")
    company_website = serializers.URLField(required=False, allow_blank=True, help_text="Site web de l'entreprise")
    company_tax_number = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text="Numéro de TVA")
    company_registration_number = serializers.CharField(max_length=50, required=False, allow_blank=True, help_text="Numéro d'enregistrement (SIRET)")
    company_logo = serializers.ImageField(required=False, allow_null=True, help_text="Logo de l'entreprise")
    company_primary_color = serializers.CharField(max_length=7, required=False, default='#007bff', help_text="Couleur principale de l'entreprise (format hexadécimal, ex: #007bff)")

    def validate_username(self, value):
        """Validation du nom d'utilisateur"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return value

    def validate_email(self, value):
        """Validation de l'email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate(self, data):
        """Validation croisée des mots de passe et des champs entreprise"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        
        # Validation des champs entreprise requis
        required_company_fields = [
            'company_name', 'company_phone', 'company_city'
        ]
        
        for field in required_company_fields:
            if not data.get(field) or data.get(field).strip() == '':
                raise serializers.ValidationError(f"Le champ {field.replace('company_', '')} de l'entreprise est requis.")
        
        return data

    def create(self, validated_data):
        """Créer un nouvel utilisateur et son entreprise"""
        from .models import Company
        
        # Séparer les données utilisateur et entreprise
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'password': validated_data['password'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
        }
        
        company_data = {
            'name': validated_data['company_name'],
            'description': validated_data.get('company_description', ''),
            'phone': validated_data.get('company_phone', ''),
            'address': validated_data.get('company_address', ''),
            'city': validated_data.get('company_city', ''),
            'postal_code': validated_data.get('company_postal_code', ''),
            'country': validated_data.get('company_country', 'France'),
            'website': validated_data.get('company_website', ''),
            'tax_number': validated_data.get('company_tax_number', ''),
            'registration_number': validated_data.get('company_registration_number', ''),
            'logo': validated_data.get('company_logo'),
            'primary_color': validated_data.get('company_primary_color', '#007bff'),
        }
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_active=True
        )
        
        # Créer l'entreprise
        company = Company.objects.create(
            name=company_data['name'],
            email=user_data['email'],  # Utiliser l'email de l'utilisateur comme email de l'entreprise
            description=company_data['description'],
            phone=company_data['phone'],
            address=company_data['address'],
            city=company_data['city'],
            postal_code=company_data.get('postal_code', ''),
            country=company_data['country'],
            website=company_data.get('website', ''),
            tax_number=company_data.get('tax_number', ''),
            registration_number=company_data.get('registration_number', ''),
            logo=company_data.get('logo'),
            primary_color=company_data.get('primary_color', '#007bff'),
        )
        
        # Créer le profil utilisateur avec la relation à l'entreprise
        from .models import UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            company=company,
            is_company_admin=True,  # Le créateur de l'entreprise est admin
        )
        
        # Stocker l'entreprise et le profil dans l'instance pour pouvoir y accéder dans la vue
        user._created_company = company
        user._created_profile = user_profile
        
        return user


class InviteUserSerializer(serializers.Serializer):
    """
    Serializer pour l'invitation d'un nouvel utilisateur à une entreprise
    """
    email = serializers.EmailField(help_text="Email de l'utilisateur à inviter")
    first_name = serializers.CharField(max_length=30, help_text="Prénom de l'utilisateur")
    last_name = serializers.CharField(max_length=30, help_text="Nom de famille de l'utilisateur")
    role = serializers.CharField(max_length=100, help_text="Rôle à attribuer à l'utilisateur")
    company_id = serializers.IntegerField(help_text="ID de l'entreprise")
    send_email = serializers.BooleanField(default=True, help_text="Envoyer l'email d'invitation")

    def validate_email(self, value):
        """Validation de l'email"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_role(self, value):
        """Validation du rôle"""
        from apps.permissions.models import Role
        if not Role.objects.filter(name=value, is_active=True).exists():
            raise serializers.ValidationError(f"Le rôle '{value}' n'existe pas ou n'est pas actif.")
        return value

    def validate_company_id(self, value):
        """Validation de l'entreprise"""
        from .models import Company
        if not Company.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError(f"L'entreprise avec l'ID {value} n'existe pas ou n'est pas active.")
        return value

    def create(self, validated_data):
        """Créer un nouvel utilisateur invité"""
        import secrets
        import string
        from django.contrib.auth.models import User
        from apps.permissions.models import Role, UserRole
        from .models import Company
        
        # Générer un mot de passe temporaire (secrets.choices n'existe pas en stdlib)
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=validated_data['email'],  # Utiliser l'email comme username
            email=validated_data['email'],
            password=temp_password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_active=True
        )
        
        # Récupérer le rôle et l'entreprise
        role = Role.objects.get(name=validated_data['role'])
        company = Company.objects.get(id=validated_data['company_id'])
        
        # Attribuer le rôle à l'utilisateur
        UserRole.objects.create(
            user=user,
            role=role,
            is_active=True,
            notes=f'Invitation par {self.context["request"].user.username} pour l\'entreprise {company.name}'
        )
        
        # Créer le profil utilisateur avec la relation à l'entreprise
        from .models import UserProfile
        user_profile = UserProfile.objects.create(
            user=user,
            company=company,
            is_company_admin=False,  # L'utilisateur invité n'est pas admin par défaut
        )
        
        # Stocker les informations pour l'email
        user._temp_password = temp_password
        user._company = company
        user._invited_by = self.context["request"].user
        user._created_profile = user_profile
        
        return user


class CompanySerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Company
    """
    user_count = serializers.SerializerMethodField()
    admin_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'logo', 'logo_url', 'primary_color', 'description', 'email', 'phone',
            'address', 'city', 'postal_code', 'country', 'website',
            'tax_number', 'registration_number', 'is_active', 'settings',
            'user_count', 'admin_count', 'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user_count', 'admin_count', 'logo_url', 'full_address']

    def get_user_count(self, obj):
        """Retourne le nombre d'utilisateurs de l'entreprise"""
        return obj.userprofile_set.count()

    def get_admin_count(self, obj):
        """Retourne le nombre d'admins de l'entreprise"""
        return obj.userprofile_set.filter(is_company_admin=True).count()

    def get_logo_url(self, obj):
        """Retourne l'URL du logo si il existe"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None

    def get_full_address(self, obj):
        """Retourne l'adresse complète formatée"""
        return obj.full_address


class CompanyListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des entreprises (version allégée)
    """
    user_count = serializers.SerializerMethodField()
    logo_url = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'logo_url', 'primary_color', 'email', 'phone', 'city', 'country',
            'is_active', 'user_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'user_count', 'logo_url']

    def get_user_count(self, obj):
        """Retourne le nombre d'utilisateurs de l'entreprise"""
        return obj.userprofile_set.count()

    def get_logo_url(self, obj):
        """Retourne l'URL du logo si il existe"""
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer pour la demande de reset de mot de passe
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """Validation de l'email"""
        if not value:
            raise serializers.ValidationError("L'email est requis.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer pour la confirmation du reset de mot de passe
    """
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    new_password_confirm = serializers.CharField(min_length=8)

    def validate(self, data):
        """Validation croisée des mots de passe"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("Les nouveaux mots de passe ne correspondent pas.")
        return data


class AlertSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Alert
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message', 'alert_type', 'alert_type_display',
            'priority', 'priority_display', 'status', 'status_display',
            'is_read', 'user', 'user_name', 'related_object_type',
            'related_object_id', 'action_url', 'action_label',
            'expires_at', 'metadata', 'is_expired', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired']

    def create(self, validated_data):
        """Créer une nouvelle alerte"""
        return Alert.objects.create(**validated_data)


class AlertCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'alertes
    """
    class Meta:
        model = Alert
        fields = [
            'title', 'message', 'alert_type', 'priority', 'user',
            'related_object_type', 'related_object_id', 'action_url',
            'action_label', 'expires_at', 'metadata'
        ]

    def create(self, validated_data):
        """Créer une nouvelle alerte"""
        return Alert.objects.create(**validated_data)


class AlertUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour d'alertes
    """
    class Meta:
        model = Alert
        fields = [
            'title', 'message', 'priority', 'status', 'is_read',
            'action_url', 'action_label', 'expires_at', 'metadata'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Notification
    """
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    notification_type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'notification_type_display',
            'priority', 'priority_display', 'status', 'status_display',
            'is_read', 'user', 'user_name', 'related_object_type',
            'related_object_id', 'action_url', 'action_label',
            'read_at', 'expires_at', 'metadata', 'is_expired',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_expired', 'read_at']

    def create(self, validated_data):
        """Créer une nouvelle notification"""
        return Notification.objects.create(**validated_data)


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création de notifications
    """
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'notification_type', 'priority', 'user',
            'related_object_type', 'related_object_id', 'action_url',
            'action_label', 'expires_at', 'metadata'
        ]

    def create(self, validated_data):
        """Créer une nouvelle notification"""
        return Notification.objects.create(**validated_data)


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la mise à jour de notifications
    """
    class Meta:
        model = Notification
        fields = [
            'title', 'message', 'priority', 'status', 'is_read',
            'action_url', 'action_label', 'expires_at', 'metadata'
        ]
