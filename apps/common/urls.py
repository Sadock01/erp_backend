# URLs communes
from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.login, name='login'),
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    path('auth/refresh-token/', views.refresh_token, name='refresh_token'),
    path('auth/invite-user/', views.invite_user, name='invite_user'),
    
    # Entreprises
    path('companies/', views.list_companies, name='list_companies'),
    path('companies/my/', views.get_my_company, name='get_my_company'),
    path('companies/<int:company_id>/', views.get_company, name='get_company'),
    
    # Reset de mot de passe
    path('auth/password-reset-request/', views.password_reset_request, name='password_reset_request'),
    path('auth/password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),
    
    # Alertes
    path('alerts/', views.alerts_list, name='alerts_list'),
    path('alerts/<int:alert_id>/', views.alert_detail, name='alert_detail'),
    path('alerts/create/', views.alert_create, name='alert_create'),
    path('alerts/<int:alert_id>/update/', views.alert_update, name='alert_update'),
    path('alerts/<int:alert_id>/delete/', views.alert_delete, name='alert_delete'),
    path('alerts/<int:alert_id>/mark-read/', views.alert_mark_read, name='alert_mark_read'),
    path('alerts/mark-all-read/', views.alerts_mark_all_read, name='alerts_mark_all_read'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('notifications/<int:notification_id>/update/', views.notification_update, name='notification_update'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notifications_mark_all_read, name='notifications_mark_all_read'),
]
