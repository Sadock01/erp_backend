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

# --- Tunnels publics (ngrok, etc.) : éviter DisallowedHost ---
# En local / préprod, accepter tous les Host headers (requis quand l’URL publique
# ne correspond pas à localhost). En production, ne force « * » que si tu le
# demandes explicitement dans .env : ALLOW_ALL_HOSTS=1 (true/yes/1 selon decouple)
# ⚠️ Ne laisse pas ALLOW_ALL_HOSTS=1 en prod Internet sans savoir ce que tu fais.
_allow_all_hosts = config('ALLOW_ALL_HOSTS', default=False, cast=bool)
if ENVIRONMENT != 'production' or _allow_all_hosts:
    ALLOWED_HOSTS = ['*']
