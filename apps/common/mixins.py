from rest_framework.response import Response
from rest_framework import status
from apps.permissions.decorators import user_has_permission


class CompanyFilterMixin:
    """
    Mixin pour filtrer automatiquement les données par Company
    """
    
    def get_queryset(self):
        """
        Filtre le queryset par l'entreprise de l'utilisateur connecté
        """
        queryset = super().get_queryset()
        
        # Super Admin peut voir toutes les entreprises
        if user_has_permission(self.request.user, 'companies_view_all'):
            return queryset
        
        # Sinon, seulement son entreprise
        try:
            user_company = self.request.user.userprofile.company
            return queryset.filter(company=user_company)
        except:
            # Si l'utilisateur n'a pas de profil, retourner un queryset vide
            return queryset.none()
    
    def perform_create(self, serializer):
        """
        Assigner automatiquement l'entreprise lors de la création
        """
        print(f"DEBUG: perform_create appelé pour {self.__class__.__name__}")
        try:
            user_company = self.request.user.userprofile.company
            print(f"DEBUG: user_company = {user_company} (ID: {user_company.id})")
            serializer.save(company=user_company)
            print("DEBUG: serializer.save() réussi")
        except Exception as e:
            print(f"DEBUG: Erreur dans perform_create: {e}")
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                'error': 'Profil utilisateur non trouvé',
                'detail': 'Vous devez être associé à une entreprise pour créer des données'
            })