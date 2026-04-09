from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Role, Permission, RolePermission, UserRole, PermissionLog


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Permission
    """
    full_codename = serializers.ReadOnlyField()

    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'codename', 'description', 'app_label', 
            'action', 'resource', 'is_active', 'is_system', 
            'full_codename', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des permissions
    """
    full_codename = serializers.ReadOnlyField()

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'app_label', 'action', 'resource', 'full_codename']


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle Role
    """
    user_count = serializers.ReadOnlyField()
    permission_count = serializers.ReadOnlyField()

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_active', 'is_system', 
            'level', 'color', 'icon', 'user_count', 'permission_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des rôles
    """
    user_count = serializers.ReadOnlyField()

    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'level', 'color', 'icon', 'user_count', 'is_active']


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle RolePermission
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_codename = serializers.CharField(source='permission.codename', read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'permission', 'granted', 'conditions', 'notes',
            'role_name', 'permission_name', 'permission_codename',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour les utilisateurs
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle UserRole
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    role_color = serializers.CharField(source='role.color', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.username', read_only=True)
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()

    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'role', 'assigned_by', 'assigned_at', 'expires_at',
            'is_active', 'notes', 'user_name', 'user_email', 'role_name', 
            'role_color', 'assigned_by_name', 'is_expired', 'days_until_expiry',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'assigned_at', 'created_at', 'updated_at']


class UserRoleCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour créer un UserRole
    """
    class Meta:
        model = UserRole
        fields = ['user', 'role', 'expires_at', 'notes']

    def create(self, validated_data):
        # L'utilisateur qui assigne le rôle est l'utilisateur connecté
        validated_data['assigned_by'] = self.context['request'].user
        return super().create(validated_data)


class PermissionLogSerializer(serializers.ModelSerializer):
    """
    Serializer pour le modèle PermissionLog
    """
    user_name = serializers.CharField(source='user.username', read_only=True)
    target_user_name = serializers.CharField(source='target_user.username', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)

    class Meta:
        model = PermissionLog
        fields = [
            'id', 'user', 'action', 'target_user', 'role', 'permission',
            'details', 'ip_address', 'user_agent', 'user_name', 
            'target_user_name', 'role_name', 'permission_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserPermissionsSerializer(serializers.Serializer):
    """
    Serializer pour récupérer les permissions d'un utilisateur
    """
    user = UserSerializer(read_only=True)
    roles = RoleListSerializer(many=True, read_only=True)
    permissions = PermissionListSerializer(many=True, read_only=True)
    total_permissions = serializers.IntegerField(read_only=True)
    total_roles = serializers.IntegerField(read_only=True)


class RolePermissionsSerializer(serializers.Serializer):
    """
    Serializer pour récupérer les permissions d'un rôle
    """
    role = RoleSerializer(read_only=True)
    permissions = PermissionListSerializer(many=True, read_only=True)
    granted_permissions = PermissionListSerializer(many=True, read_only=True)
    denied_permissions = PermissionListSerializer(many=True, read_only=True)
    total_permissions = serializers.IntegerField(read_only=True)


class AssignRoleSerializer(serializers.Serializer):
    """
    Serializer pour assigner un rôle à un utilisateur
    """
    user_id = serializers.IntegerField()
    role_id = serializers.IntegerField()
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_user_id(self, value):
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur introuvable")
        return value

    def validate_role_id(self, value):
        try:
            Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Rôle introuvable")
        return value


class GrantPermissionSerializer(serializers.Serializer):
    """
    Serializer pour accorder une permission à un rôle
    """
    role_id = serializers.IntegerField()
    permission_id = serializers.IntegerField()
    granted = serializers.BooleanField(default=True)
    conditions = serializers.JSONField(required=False, default=dict)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_role_id(self, value):
        try:
            Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Rôle introuvable")
        return value

    def validate_permission_id(self, value):
        try:
            Permission.objects.get(id=value)
        except Permission.DoesNotExist:
            raise serializers.ValidationError("Permission introuvable")
        return value


class BulkAssignRoleSerializer(serializers.Serializer):
    """
    Serializer pour assigner un rôle à plusieurs utilisateurs
    """
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    role_id = serializers.IntegerField()
    expires_at = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_user_ids(self, value):
        if len(value) != User.objects.filter(id__in=value).count():
            raise serializers.ValidationError("Certains utilisateurs n'existent pas")
        return value

    def validate_role_id(self, value):
        try:
            Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Rôle introuvable")
        return value


class PermissionStatsSerializer(serializers.Serializer):
    """
    Serializer pour les statistiques des permissions
    """
    total_users = serializers.IntegerField()
    total_roles = serializers.IntegerField()
    total_permissions = serializers.IntegerField()
    active_roles = serializers.IntegerField()
    system_roles = serializers.IntegerField()
    users_by_role = serializers.DictField()
    permissions_by_app = serializers.DictField()
    recent_assignments = UserRoleSerializer(many=True)
    recent_logs = PermissionLogSerializer(many=True)


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer pour la création d'utilisateurs par un admin
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    role_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True,
        help_text="Liste des IDs des rôles à assigner à l'utilisateur"
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm', 
            'first_name', 'last_name', 'is_active', 'is_staff', 
            'is_superuser', 'role_ids'
        ]

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
        """Validation croisée des mots de passe"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Les mots de passe ne correspondent pas.")
        return data

    def create(self, validated_data):
        """Créer un nouvel utilisateur avec rôles optionnels"""
        # Extraire les rôles
        role_ids = validated_data.pop('role_ids', [])
        password_confirm = validated_data.pop('password_confirm')
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False),
            is_superuser=validated_data.get('is_superuser', False)
        )
        
        # Assigner les rôles si fournis
        if role_ids:
            request = self.context.get('request')
            if request and request.user:
                for role_id in role_ids:
                    try:
                        role = Role.objects.get(id=role_id)
                        UserRole.objects.create(
                            user=user,
                            role=role,
                            assigned_by=request.user,
                            is_active=True,
                            notes=f'Rôle assigné lors de la création de l\'utilisateur'
                        )
                    except Role.DoesNotExist:
                        # Ignorer les rôles inexistants
                        pass
        
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer simplifié pour la liste des utilisateurs
    """
    roles_count = serializers.SerializerMethodField()
    last_login_display = serializers.SerializerMethodField()
    date_joined_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'roles_count', 'last_login_display', 'date_joined_display'
        ]

    def get_roles_count(self, obj):
        """Nombre de rôles actifs de l'utilisateur"""
        return UserRole.objects.filter(user=obj, is_active=True).count()

    def get_last_login_display(self, obj):
        """Affichage formaté de la dernière connexion"""
        if obj.last_login:
            return obj.last_login.strftime('%d/%m/%Y %H:%M')
        return 'Jamais connecté'

    def get_date_joined_display(self, obj):
        """Affichage formaté de la date d'inscription"""
        return obj.date_joined.strftime('%d/%m/%Y %H:%M')
