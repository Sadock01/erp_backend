"""
Configuration pour l'environnement de développement local
"""
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Configuration ALLOWED_HOSTS pour le développement
if DEBUG:
    # En mode debug, accepter tous les domaines
    ALLOWED_HOSTS = ['*']
else:
    # En production, spécifier les domaines autorisés
    ALLOWED_HOSTS = [
        'localhost', 
        '127.0.0.1',
        # Accepter tous les domaines ngrok
        '.ngrok-free.app',
        '.ngrok.io',
        '.ngrok.app',
        # Ajouter d'autres domaines de production si nécessaire
    ]

# Configuration pour le développement
CORS_ALLOW_ALL_ORIGINS = True

# Logging pour le développement
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
