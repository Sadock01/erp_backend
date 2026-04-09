# Configuration pour utiliser les settings par environnement
import os
from decouple import config

# Détermine l'environnement (local, production, etc.)
ENVIRONMENT = config('ENVIRONMENT', default='local')

# Importe les settings appropriés
if ENVIRONMENT == 'production':
    from .settings.production import *
else:
    from .settings.local import *
