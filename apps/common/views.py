# Vues communes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from .serializers import (
    UserSerializer,
    UserSelfUpdateSerializer,
    LoginSerializer,
    RegisterSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    CompanySerializer,
    CompanyMyUpdateSerializer,
    AlertSerializer,
    AlertCreateSerializer,
    AlertUpdateSerializer,
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationUpdateSerializer,
)
from .models import PasswordResetCode, Alert, Notification
from django.core.paginator import Paginator
from django.db.models import Q


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur avec création d'entreprise et attribution automatique du rôle Admin
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = Token.objects.create(user=user)
        
        # Récupérer l'entreprise créée
        company = getattr(user, '_created_company', None)
        
        # Attribuer automatiquement le rôle Admin (créé par migration permissions.0002)
        try:
            from apps.permissions.models import Role, UserRole
            admin_role, _ = Role.objects.get_or_create(
                name='Admin',
                defaults={
                    'description': 'Administrateur de l’entreprise (accès complet application).',
                    'is_active': True,
                    'is_system': True,
                    'level': 0,
                    'color': '#dc3545',
                    'icon': 'fas fa-user-shield',
                },
            )
            UserRole.objects.get_or_create(
                user=user,
                role=admin_role,
                defaults={
                    'is_active': True,
                    'notes': 'Attribué automatiquement lors de l\'inscription',
                },
            )
        except Exception as e:
            print(f"Erreur lors de l'attribution du rôle Admin: {e}")
        
        user_serializer = UserSerializer(user)
        
        # Préparer la réponse avec les informations de l'entreprise
        response_data = {
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Inscription réussie, entreprise créée et rôle Admin attribué'
        }
        
        # Ajouter les informations de l'entreprise si elle a été créée
        if company:
            response_data['company'] = {
                'id': company.id,
                'name': company.name,
                'email': company.email,
                'description': company.description,
                'phone': company.phone,
                'address': company.address,
                'city': company.city,
                'postal_code': company.postal_code,
                'country': company.country,
                'website': company.website,
                'tax_number': company.tax_number,
                'registration_number': company.registration_number,
                'logo': company.logo.url if company.logo else None,
                'primary_color': company.primary_color,
                'is_active': company.is_active,
                'created_at': company.created_at,
            }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_user(request):
    """
    Inviter un nouvel utilisateur à rejoindre une entreprise
    Nécessite d'être authentifié et d'avoir les permissions d'admin
    """
    from .serializers import InviteUserSerializer
    from apps.permissions.decorators import user_has_permission
    
    # Vérifier que l'utilisateur a la permission d'inviter des utilisateurs
    if not user_has_permission(request.user, 'users_manage'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission d\'inviter des utilisateurs',
            'required_permission': 'users_manage'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = InviteUserSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        user = serializer.save()
        
        # Préparer la réponse
        response_data = {
            'message': 'Utilisateur invité avec succès',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
            },
            'company': {
                'id': user._company.id,
                'name': user._company.name,
            },
            'role': serializer.validated_data['role'],
            'temp_password': user._temp_password if not serializer.validated_data['send_email'] else None,
        }
        
        # Envoyer l'email si demandé
        if serializer.validated_data['send_email']:
            try:
                send_invitation_email(user, user._temp_password, user._company, user._invited_by)
                response_data['email_sent'] = True
                response_data['message'] += ' et email d\'invitation envoyé'
            except Exception as e:
                response_data['email_sent'] = False
                response_data['email_error'] = str(e)
                response_data['temp_password'] = user._temp_password  # Fournir le mot de passe en cas d'erreur email
        else:
            response_data['email_sent'] = False
            response_data['message'] += ' (email non envoyé)'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_invitation_email(user, temp_password, company, invited_by):
    """
    Envoyer un email d'invitation à l'utilisateur
    """
    from django.core.mail import send_mail
    from django.conf import settings
    
    subject = f"Invitation à rejoindre {company.name} sur Nodus ERP"
    
    message = f"""
Bonjour {user.first_name} {user.last_name},

Vous avez été invité(e) par {invited_by.get_full_name()} à rejoindre l'entreprise "{company.name}" sur Nodus ERP.

Vos identifiants de connexion temporaires :
- Email : {user.email}
- Mot de passe temporaire : {temp_password}

IMPORTANT : Vous devrez changer ce mot de passe lors de votre première connexion.

Pour vous connecter, rendez-vous sur : {getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')}/login

Cordialement,
L'équipe Nodus ERP
    """
    
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@nodus-erp.com'),
        recipient_list=[user.email],
        fail_silently=False,
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_company(request, company_id):
    """
    Récupérer les informations d'une entreprise
    Nécessite d'être authentifié
    """
    from .models import Company, UserProfile
    from apps.permissions.decorators import user_has_permission
    
    try:
        company = Company.objects.get(id=company_id, is_active=True)
    except Company.DoesNotExist:
        return Response({
            'error': 'Entreprise non trouvée',
            'detail': f'L\'entreprise avec l\'ID {company_id} n\'existe pas ou n\'est pas active'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Vérifier que l'utilisateur a accès à cette entreprise
    try:
        user_profile = UserProfile.objects.get(user=request.user, company=company)
    except UserProfile.DoesNotExist:
        # Vérifier si l'utilisateur a la permission de voir toutes les entreprises
        if not user_has_permission(request.user, 'companies_view_all'):
            return Response({
                'error': 'Accès refusé',
                'detail': 'Vous n\'avez pas accès à cette entreprise'
            }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CompanySerializer(company, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def get_my_company(request):
    """
    Entreprise liée au UserProfile : GET lecture, PATCH/PUT mise à jour (boutique).
    """
    from .models import UserProfile

    try:
        user_profile = UserProfile.objects.select_related('company').get(user=request.user)
        company = user_profile.company
    except UserProfile.DoesNotExist:
        return Response({
            'error': 'Profil non trouvé',
            'detail': 'Vous n\'êtes associé à aucune entreprise'
        }, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CompanySerializer(company, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    partial = request.method == 'PATCH'
    write_serializer = CompanyMyUpdateSerializer(
        company,
        data=request.data,
        partial=partial,
        context={'request': request},
    )
    if write_serializer.is_valid():
        write_serializer.save()
        company.refresh_from_db()
        return Response(
            CompanySerializer(company, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )
    return Response(write_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_companies(request):
    """
    Lister toutes les entreprises (nécessite permission spéciale)
    Nécessite d'être authentifié et d'avoir la permission companies_view_all
    """
    from .models import Company
    from .serializers import CompanyListSerializer
    from apps.permissions.decorators import user_has_permission
    
    # Vérifier la permission
    if not user_has_permission(request.user, 'companies_view_all'):
        return Response({
            'error': 'Permission refusée',
            'detail': 'Vous n\'avez pas la permission de voir toutes les entreprises',
            'required_permission': 'companies_view_all'
        }, status=status.HTTP_403_FORBIDDEN)
    
    companies = Company.objects.filter(is_active=True).order_by('name')
    serializer = CompanyListSerializer(companies, many=True, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Authentification d'un utilisateur avec email et génération d'un token
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Trouver l'utilisateur par email
        try:
            user = User.objects.get(email=email)
            # Authentifier avec le username (Django utilise username pour authenticate)
            user = authenticate(username=user.username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                user_serializer = UserSerializer(user)
                return Response({
                    'token': token.key,
                    'user': user_serializer.data,
                    'message': 'Connexion réussie'
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Email ou mot de passe incorrect'
                }, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({
                'error': 'Email ou mot de passe incorrect'
            }, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    Déconnexion d'un utilisateur (suppression du token)
    """
    try:
        request.user.auth_token.delete()
        return Response({
            'message': 'Déconnexion réussie'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Erreur lors de la déconnexion'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Profil de l'utilisateur connecté : GET lecture, PATCH/PUT mise à jour partielle ou complète.
    """
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    partial = request.method == 'PATCH'
    serializer = UserSelfUpdateSerializer(
        request.user,
        data=request.data,
        partial=partial,
    )
    if serializer.is_valid():
        serializer.save()
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def refresh_token(request):
    """
    Régénérer un nouveau token pour l'utilisateur connecté
    """
    try:
        # Supprimer l'ancien token
        request.user.auth_token.delete()
        # Créer un nouveau token
        token = Token.objects.create(user=request.user)
        user_serializer = UserSerializer(request.user)
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Token régénéré avec succès'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Erreur lors de la régénération du token'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """
    Demander un reset de mot de passe
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Désactiver les anciens codes pour cet email
            PasswordResetCode.objects.filter(
                email=email,
                is_used=False
            ).update(is_used=True)
            
            # Créer un nouveau code
            reset_code = PasswordResetCode.objects.create(
                user=user,
                email=email
            )
            
            # Simuler l'envoi d'email - afficher le code dans le terminal
            print(f"\n{'='*60}")
            print(f"🔐 CODE DE RESET DE MOT DE PASSE")
            print(f"{'='*60}")
            print(f"Email: {email}")
            print(f"Code: {reset_code.code}")
            print(f"Expire dans: 15 minutes")
            print(f"{'='*60}\n")
            
            return Response({
                'message': 'Code de vérification envoyé par email',
                'email': email,
                'expires_in': 15  # minutes
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            # Pour la sécurité, on ne révèle pas si l'email existe ou non
            return Response({
                'message': 'Si cet email existe, un code de vérification a été envoyé',
                'email': email,
                'expires_in': 15
            }, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """
    Confirmer le reset de mot de passe avec le code
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        try:
            # Trouver le code valide
            reset_code = PasswordResetCode.objects.get(
                email=email,
                code=code,
                is_used=False
            )
            
            # Vérifier si le code est valide
            if not reset_code.is_valid():
                reset_code.increment_attempts()
                return Response({
                    'error': 'Code invalide, expiré ou déjà utilisé'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier le code
            if reset_code.code != code:
                reset_code.increment_attempts()
                return Response({
                    'error': 'Code incorrect'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Mettre à jour le mot de passe
            user = reset_code.user
            user.set_password(new_password)
            user.save()
            
            # Marquer le code comme utilisé
            reset_code.mark_as_used()
            
            # Supprimer tous les tokens existants de l'utilisateur
            Token.objects.filter(user=user).delete()
            
            print(f"\n{'='*60}")
            print(f"✅ MOT DE PASSE RÉINITIALISÉ AVEC SUCCÈS")
            print(f"{'='*60}")
            print(f"Email: {email}")
            print(f"Utilisateur: {user.username}")
            print(f"Date: {timezone.now()}")
            print(f"{'='*60}\n")
            
            return Response({
                'message': 'Mot de passe réinitialisé avec succès',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
            
        except PasswordResetCode.DoesNotExist:
            return Response({
                'error': 'Code de vérification invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==================== ALERTES ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alerts_list(request):
    """
    Liste des alertes avec pagination et filtres
    """
    try:
        # Paramètres de pagination
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        # Filtres
        alert_type = request.GET.get('type')
        priority = request.GET.get('priority')
        status_filter = request.GET.get('status')
        is_read = request.GET.get('is_read')
        user_id = request.GET.get('user_id')
        
        # Requête de base
        queryset = Alert.objects.all()
        
        # Filtres
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page_obj = paginator.get_page(page)
        
        # Sérialisation
        serializer = AlertSerializer(page_obj, many=True)
        
        # Résumé
        summary = {
            'total': paginator.count,
            'page': page,
            'pages': paginator.num_pages,
            'per_page': limit,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'unread_count': Alert.objects.filter(is_read=False).count(),
            'by_priority': {
                'low': Alert.objects.filter(priority='low').count(),
                'medium': Alert.objects.filter(priority='medium').count(),
                'high': Alert.objects.filter(priority='high').count(),
                'critical': Alert.objects.filter(priority='critical').count(),
            },
            'by_status': {
                'active': Alert.objects.filter(status='active').count(),
                'read': Alert.objects.filter(status='read').count(),
                'resolved': Alert.objects.filter(status='resolved').count(),
                'dismissed': Alert.objects.filter(status='dismissed').count(),
            }
        }
        
        return Response({
            'success': True,
            'data': serializer.data,
            'summary': summary,
            'message': 'Alertes récupérées avec succès'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERTS_LIST_ERROR',
                'message': 'Erreur lors de la récupération des alertes',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_detail(request, alert_id):
    """
    Détails d'une alerte
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        serializer = AlertSerializer(alert)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Alerte récupérée avec succès'
        })
        
    except Alert.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_NOT_FOUND',
                'message': 'Alerte non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_DETAIL_ERROR',
                'message': 'Erreur lors de la récupération de l\'alerte',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def alert_create(request):
    """
    Créer une nouvelle alerte
    """
    try:
        serializer = AlertCreateSerializer(data=request.data)
        if serializer.is_valid():
            alert = serializer.save()
            response_serializer = AlertSerializer(alert)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Alerte créée avec succès'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'ALERT_CREATE_ERROR',
                    'message': 'Erreur de validation',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_CREATE_ERROR',
                'message': 'Erreur lors de la création de l\'alerte',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def alert_update(request, alert_id):
    """
    Mettre à jour une alerte
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        
        # Utiliser PATCH pour mise à jour partielle
        partial = request.method == 'PATCH'
        serializer = AlertUpdateSerializer(alert, data=request.data, partial=partial)
        
        if serializer.is_valid():
            alert = serializer.save()
            response_serializer = AlertSerializer(alert)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Alerte mise à jour avec succès'
            })
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'ALERT_UPDATE_ERROR',
                    'message': 'Erreur de validation',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Alert.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_NOT_FOUND',
                'message': 'Alerte non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_UPDATE_ERROR',
                'message': 'Erreur lors de la mise à jour de l\'alerte',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def alert_delete(request, alert_id):
    """
    Supprimer une alerte
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.delete()
        
        return Response({
            'success': True,
            'message': 'Alerte supprimée avec succès'
        })
        
    except Alert.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_NOT_FOUND',
                'message': 'Alerte non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_DELETE_ERROR',
                'message': 'Erreur lors de la suppression de l\'alerte',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def alert_mark_read(request, alert_id):
    """
    Marquer une alerte comme lue
    """
    try:
        alert = Alert.objects.get(id=alert_id)
        alert.mark_as_read()
        
        serializer = AlertSerializer(alert)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Alerte marquée comme lue'
        })
        
    except Alert.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_NOT_FOUND',
                'message': 'Alerte non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERT_MARK_READ_ERROR',
                'message': 'Erreur lors du marquage de l\'alerte',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def alerts_mark_all_read(request):
    """
    Marquer toutes les alertes comme lues
    """
    try:
        # Paramètres de filtrage
        alert_type = request.GET.get('type')
        priority = request.GET.get('priority')
        user_id = request.GET.get('user_id')
        
        # Requête de base
        queryset = Alert.objects.filter(is_read=False)
        
        # Filtres
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Marquer comme lues
        updated_count = queryset.update(is_read=True, status='read')
        
        return Response({
            'success': True,
            'data': {
                'updated_count': updated_count
            },
            'message': f'{updated_count} alertes marquées comme lues'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'ALERTS_MARK_ALL_READ_ERROR',
                'message': 'Erreur lors du marquage des alertes',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== NOTIFICATIONS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_list(request):
    """
    Liste des notifications avec pagination et filtres
    """
    try:
        # Paramètres de pagination
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        
        # Filtres
        notification_type = request.GET.get('type')
        priority = request.GET.get('priority')
        status_filter = request.GET.get('status')
        is_read = request.GET.get('is_read')
        user_id = request.GET.get('user_id')
        
        # Requête de base
        queryset = Notification.objects.all()
        
        # Filtres
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Pagination
        paginator = Paginator(queryset, limit)
        page_obj = paginator.get_page(page)
        
        # Sérialisation
        serializer = NotificationSerializer(page_obj, many=True)
        
        # Résumé
        summary = {
            'total': paginator.count,
            'page': page,
            'pages': paginator.num_pages,
            'per_page': limit,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'unread_count': Notification.objects.filter(is_read=False).count(),
            'by_priority': {
                'low': Notification.objects.filter(priority='low').count(),
                'medium': Notification.objects.filter(priority='medium').count(),
                'high': Notification.objects.filter(priority='high').count(),
                'urgent': Notification.objects.filter(priority='urgent').count(),
            },
            'by_status': {
                'unread': Notification.objects.filter(status='unread').count(),
                'read': Notification.objects.filter(status='read').count(),
                'archived': Notification.objects.filter(status='archived').count(),
            }
        }
        
        return Response({
            'success': True,
            'data': serializer.data,
            'summary': summary,
            'message': 'Notifications récupérées avec succès'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATIONS_LIST_ERROR',
                'message': 'Erreur lors de la récupération des notifications',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_detail(request, notification_id):
    """
    Détails d'une notification
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        serializer = NotificationSerializer(notification)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Notification récupérée avec succès'
        })
        
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_NOT_FOUND',
                'message': 'Notification non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_DETAIL_ERROR',
                'message': 'Erreur lors de la récupération de la notification',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_create(request):
    """
    Créer une nouvelle notification
    """
    try:
        serializer = NotificationCreateSerializer(data=request.data)
        if serializer.is_valid():
            notification = serializer.save()
            response_serializer = NotificationSerializer(notification)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Notification créée avec succès'
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOTIFICATION_CREATE_ERROR',
                    'message': 'Erreur de validation',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_CREATE_ERROR',
                'message': 'Erreur lors de la création de la notification',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def notification_update(request, notification_id):
    """
    Mettre à jour une notification
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Utiliser PATCH pour mise à jour partielle
        partial = request.method == 'PATCH'
        serializer = NotificationUpdateSerializer(notification, data=request.data, partial=partial)
        
        if serializer.is_valid():
            notification = serializer.save()
            response_serializer = NotificationSerializer(notification)
            
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Notification mise à jour avec succès'
            })
        else:
            return Response({
                'success': False,
                'error': {
                    'code': 'NOTIFICATION_UPDATE_ERROR',
                    'message': 'Erreur de validation',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_NOT_FOUND',
                'message': 'Notification non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_UPDATE_ERROR',
                'message': 'Erreur lors de la mise à jour de la notification',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notification_delete(request, notification_id):
    """
    Supprimer une notification
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        
        return Response({
            'success': True,
            'message': 'Notification supprimée avec succès'
        })
        
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_NOT_FOUND',
                'message': 'Notification non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_DELETE_ERROR',
                'message': 'Erreur lors de la suppression de la notification',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, notification_id):
    """
    Marquer une notification comme lue
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        notification.mark_as_read()
        
        serializer = NotificationSerializer(notification)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'message': 'Notification marquée comme lue'
        })
        
    except Notification.DoesNotExist:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_NOT_FOUND',
                'message': 'Notification non trouvée'
            }
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATION_MARK_READ_ERROR',
                'message': 'Erreur lors du marquage de la notification',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def notifications_mark_all_read(request):
    """
    Marquer toutes les notifications comme lues
    """
    try:
        # Paramètres de filtrage
        notification_type = request.GET.get('type')
        priority = request.GET.get('priority')
        user_id = request.GET.get('user_id')
        
        # Requête de base
        queryset = Notification.objects.filter(is_read=False)
        
        # Filtres
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        if priority:
            queryset = queryset.filter(priority=priority)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Marquer comme lues
        updated_count = queryset.update(is_read=True, status='read', read_at=timezone.now())
        
        return Response({
            'success': True,
            'data': {
                'updated_count': updated_count
            },
            'message': f'{updated_count} notifications marquées comme lues'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': {
                'code': 'NOTIFICATIONS_MARK_ALL_READ_ERROR',
                'message': 'Erreur lors du marquage des notifications',
                'details': str(e)
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
