#!/usr/bin/env bash
set -Eeuo pipefail

# Deploiement Django "safe" en une commande.
# Usage simple:
#   ./deploy.sh
#
# Variables optionnelles (ajustees pour ton cas):
#   APP_DIR=/home/deployer/erp_backend
#   VENV_DIR=/home/deployer/erp_backend/venv
#   REQUIREMENTS_FILE=requirements.txt
#   DJANGO_SETTINGS_MODULE=nodus.settings
#   ENVIRONMENT=production
#   GUNICORN_SERVICE=gunicorn_erp
#   USE_SUDO=1
#   BACKUP_BEFORE_MIGRATE=1
#   BACKUP_DIR=/var/backups/nodus

APP_DIR="${APP_DIR:-/home/deployer/erp_backend}"
VENV_DIR="${VENV_DIR:-/home/deployer/erp_backend/venv}"
REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-requirements.txt}"
DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-nodus.settings}"
ENVIRONMENT="${ENVIRONMENT:-production}"
GUNICORN_SERVICE="${GUNICORN_SERVICE:-gunicorn_erp}"
USE_SUDO="${USE_SUDO:-1}"
BACKUP_BEFORE_MIGRATE="${BACKUP_BEFORE_MIGRATE:-0}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups}"

if [[ "${USE_SUDO}" == "1" ]]; then
  SUDO_BIN="sudo"
else
  SUDO_BIN=""
fi

on_error() {
  local exit_code=$?
  echo "ERREUR: deploiement interrompu (code ${exit_code})."
  exit "${exit_code}"
}
trap on_error ERR

log() {
  echo
  echo "==> $1"
}

run() {
  echo "+ $*"
  "$@"
}

log "Preparation du dossier projet"
cd "${APP_DIR}"

log "Chargement des variables d'environnement"
if [[ -f ".env" ]]; then
  # On exporte les variables du fichier .env pour qu'elles soient visibles par le script et Django
  export $(grep -v '^#' .env | xargs)
else
  echo "ATTENTION: Fichier .env introuvable !"
fi

if [[ ! -f "manage.py" ]]; then
  echo "ERREUR: manage.py introuvable dans ${APP_DIR}"
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "ERREUR: venv introuvable (${VENV_DIR})"
  exit 1
fi

if [[ ! -f "${REQUIREMENTS_FILE}" ]]; then
  echo "ERREUR: fichier ${REQUIREMENTS_FILE} introuvable"
  exit 1
fi

log "Activation du virtualenv"
# shellcheck disable=SC1090
source "${VENV_DIR}/bin/activate"

export DJANGO_SETTINGS_MODULE
export ENVIRONMENT

log "Mise a jour des dependances"
run pip install -r "${REQUIREMENTS_FILE}"

if [[ "${BACKUP_BEFORE_MIGRATE}" == "1" ]]; then
  if command -v pg_dump >/dev/null 2>&1; then
    log "Backup PostgreSQL avant migration"
    mkdir -p "${BACKUP_DIR}"
    backup_file="${BACKUP_DIR}/db_$(date +%F_%H-%M-%S).sql"
    if [[ -z "${DB_NAME:-}" || -z "${DB_USER:-}" ]]; then
      echo "ERREUR: DB_NAME et DB_USER doivent etre definis pour le backup."
      exit 1
    fi
    run pg_dump -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "${DB_USER}" "${DB_NAME}" > "${backup_file}"
    echo "Backup cree: ${backup_file}"
  else
    echo "ATTENTION: pg_dump non disponible, backup ignore."
  fi
fi

log "Checks Django (mode deploy)"
run python manage.py check --deploy

log "Verification migrations locales non committees"
run python manage.py makemigrations --check --dry-run

log "Application des migrations"
run python manage.py migrate --noinput

log "Collecte des fichiers statiques"
run python manage.py collectstatic --noinput

if command -v systemctl >/dev/null 2>&1; then
  if systemctl list-unit-files | awk '{print $1}' | grep -q "^${GUNICORN_SERVICE}\.service$"; then
    log "Redemarrage du service ${GUNICORN_SERVICE}"
    if [[ -n "${SUDO_BIN}" ]]; then
      run "${SUDO_BIN}" systemctl restart "${GUNICORN_SERVICE}"
      run "${SUDO_BIN}" systemctl status "${GUNICORN_SERVICE}" --no-pager -l
    else
      run systemctl restart "${GUNICORN_SERVICE}"
      run systemctl status "${GUNICORN_SERVICE}" --no-pager -l
    fi
  else
    echo "ATTENTION: service ${GUNICORN_SERVICE}.service introuvable. Etape restart ignoree."
  fi
else
  echo "ATTENTION: systemctl indisponible. Etape restart ignoree."
fi

log "Deploiement termine avec succes"
