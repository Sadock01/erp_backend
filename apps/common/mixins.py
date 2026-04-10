from rest_framework.response import Response
from rest_framework import status

from apps.common.tenant_scope import get_user_company_or_all, is_missing_tenant_profile


class CompanyFilterMixin:
    """
    Mixin pour filtrer automatiquement les données par Company
    """

    def get_queryset(self):
        """
        Filtre le queryset par l'entreprise de l'utilisateur connecté.
        Seul le superuser Django voit toutes les entreprises ; le rôle ERP Admin
        reste cantonné à sa Company (voir tenant_scope).
        """
        queryset = super().get_queryset()
        scope = get_user_company_or_all(self.request.user)
        if scope is None:
            return queryset
        if is_missing_tenant_profile(scope):
            return queryset.none()
        return queryset.filter(company=scope)
    
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