#!/usr/bin/env bash
# =========================================================
# One-command deploy for Django + Docker + Host MySQL
# =========================================================

set -euo pipefail
IFS=$'\n\t'

# ---------- helpers ----------
info(){ echo -e "\e[34m[INFO]\e[0m $*"; }
warn(){ echo -e "\e[33m[WARN]\e[0m $*"; }
fatal(){ echo -e "\e[31m[ERROR]\e[0m $*"; exit 1; }

# ---------- checks ----------
[ "$(id -u)" -eq 0 ] || fatal "Run this script as root (sudo ./qrdeploy.sh)"

[ -f ".env" ] || fatal ".env not found in project directory"

info "Loading .env"
set -o allexport
source .env
set +o allexport

# ---------- required env ----------
: "${DB_NAME:?DB_NAME missing in .env}"
: "${DB_USER:?DB_USER missing in .env}"
: "${DB_PASSWORD:?DB_PASSWORD missing in .env}"
: "${DB_HOST:?DB_HOST missing in .env}"
: "${DB_PORT:?DB_PORT missing in .env}"

WEB_CONTAINER="${WEB_CONTAINER:-esschert_web}"

ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-admin}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@admin.com}"

# =========================================================
# 1. Docker
# =========================================================
if ! command -v docker >/dev/null 2>&1; then
  info "Installing Docker..."
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
fi

info "Docker OK: $(docker --version)"

# =========================================================
# 2. MySQL (host)
# =========================================================
if ! command -v mysql >/dev/null 2>&1; then
  info "Installing MySQL server..."
  DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
fi

systemctl enable mysql
systemctl start mysql
info "MySQL running"

# =========================================================
# 3. Ensure DB + USER (NO root modifications!)
# =========================================================
info "Ensuring database and user exist..."

mysql -uroot <<SQL
CREATE DATABASE IF NOT EXISTS ${DB_NAME}
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS '${DB_USER}'@'%' IDENTIFIED BY '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'%';
FLUSH PRIVILEGES;
SQL

info "Database and user ready"

# =========================================================
# 4. Test MySQL connection (CRITICAL)
# =========================================================
info "Testing MySQL connection from host..."

mysql \
  -h"${DB_HOST}" \
  -P"${DB_PORT}" \
  -u"${DB_USER}" \
  -p"${DB_PASSWORD}" \
  -e "SELECT 1;" "${DB_NAME}" \
  >/dev/null 2>&1 || fatal "Cannot connect to MySQL with provided credentials"

info "MySQL connection OK"

# =========================================================
# 5. Docker Compose
# =========================================================
COMPOSE_CMD="docker compose"

info "Building containers..."
$COMPOSE_CMD build

info "Starting containers..."
$COMPOSE_CMD up -d

sleep 8

# =========================================================
# 6. Django checks
# =========================================================
docker ps --format '{{.Names}}' | grep -q "^${WEB_CONTAINER}$" \
  || fatal "Web container ${WEB_CONTAINER} not running"

info "Running migrations..."
docker exec "$WEB_CONTAINER" python manage.py migrate --noinput

info "Collecting static..."
docker exec "$WEB_CONTAINER" python manage.py collectstatic --noinput

# =========================================================
# 7. Superuser
# =========================================================
info "Ensuring Django superuser exists..."

docker exec -i "$WEB_CONTAINER" python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
u, _ = User.objects.get_or_create(username="${ADMIN_USER}")
u.email="${ADMIN_EMAIL}"
u.set_password("${ADMIN_PASS}")
u.is_staff=True
u.is_superuser=True
u.save()
print("Admin ready:", u.username)
EOF

# =========================================================
# DONE
# =========================================================
info "============================================"
info "DEPLOY FINISHED SUCCESSFULLY 🚀"
info "Admin: ${ADMIN_USER} / ${ADMIN_PASS}"
info "DB: ${DB_NAME} @ ${DB_HOST}:${DB_PORT}"
info "============================================"
