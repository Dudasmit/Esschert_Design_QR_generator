#!/usr/bin/env bash


# -------------------------
# Run this script INSIDE the project directory.
# .env must already be present.
# -------------------------

set -euo pipefail
IFS=$'\n\t'

# Add docker compose plugin to PATH for sudo
export PATH=$PATH:/usr/libexec/docker/cli-plugins:/usr/lib/docker/cli-plugins

info(){ echo -e "\e[34m[INFO]\e[0m $*"; }
warn(){ echo -e "\e[33m[WARN]\e[0m $*"; }
fatal(){ echo -e "\e[31m[ERROR]\e[0m $*"; exit 1; }

# 1. Check .env
if [ ! -f ".env" ]; then
  fatal ".env Not found in the current directory. Place .env next to the script and run again."
fi

info "Loading .env ..."
set -o allexport
source .env
set +o allexport

# Default admin creds
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASS="${ADMIN_PASS:-admin}"
ADMIN_EMAIL="${ADMIN_EMAIL:-admin@admin.com}"

# SERVICE NAME of your Django web container
WEB_CONTAINER="${WEB_CONTAINER:-inriver_web}"

# Detect DB password (if need to configure MySQL)
DB_PASS="${DB_PASSWORD:-${MYSQL_ROOT_PASSWORD:-${DB_ROOT_PASSWORD:-}}}"

###############################################
# 2. Install Docker if missing
###############################################
if ! command -v docker >/dev/null 2>&1; then
  info "Устанавливаю Docker..."
  apt-get update -y
  apt-get install -y ca-certificates curl gnupg lsb-release
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
  apt-get update -y
  apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  info "Docker installed."
else
  info "Docker already installed: $(docker --version)"
fi

###############################################
# 3. Install MySQL 8 if missing
###############################################
if ! command -v mysql >/dev/null 2>&1; then
  info "MySQL not found. Installing mysql-server..."
  export DEBIAN_FRONTEND=noninteractive
  apt-get update -y
  apt-get install -y mysql-server
else
  info "MySQL already installed: $(mysql --version)"
fi

systemctl enable mysql || true
systemctl start mysql

###############################################
# 4. Set MySQL root password (optional)
###############################################
if [ -z "${DB_PASS:-}" ]; then
  RNG="$(tr -dc A-Za-z0-9 </dev/urandom | head -c 12)"
  warn "DB_PASSWORD not found. Generated MySQL root password: $RNG"
  DB_PASS="$RNG"
fi

info "Configuring root MySQL for password login..."
if mysql -uroot -e "SELECT 1;" >/dev/null 2>&1; then
  mysql -uroot <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${DB_PASS}';
FLUSH PRIVILEGES;
SQL
  info "root password has been set."
fi

###############################################
# 5. Determine docker compose command
###############################################
if docker compose version >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
elif command -v docker-compose >/dev/null 2>&1; then
  COMPOSE_CMD="docker-compose"
else
  fatal "docker compose is missing. Make sure docker-compose-plugin is installed."
fi

###############################################
# 6. Build and run containers
###############################################
info "Running docker compose build + up ..."
$COMPOSE_CMD build
$COMPOSE_CMD up -d

info "Containers started. Waiting 10 seconds..."
sleep 10

###############################################
# 7. Apply migrations & collectstatic
###############################################
if ! docker ps --format '{{.Names}}' | grep -q "^${WEB_CONTAINER}$"; then
  fatal "Container ${WEB_CONTAINER} not found! Check docker-compose.yml"
fi

info "Applying migrations..."
docker exec -i "$WEB_CONTAINER" bash -lc "python manage.py migrate --noinput"

info "Collecting static..."
docker exec -i "$WEB_CONTAINER" bash -lc "python manage.py collectstatic --noinput"

###############################################
# 8. Create superuser
###############################################
info "Creating a superuser ($ADMIN_USER)..."

read -r -d '' PY_CREATE_ADMIN <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
u, created = User.objects.get_or_create(username="${ADMIN_USER}")
u.email = "${ADMIN_EMAIL}"
u.set_password("${ADMIN_PASS}")
u.is_staff = True
u.is_superuser = True
u.save()
print("Admin user ready: ${ADMIN_USER}")
EOF

docker exec -i "$WEB_CONTAINER" bash -lc "python manage.py shell" <<< "$PY_CREATE_ADMIN"

###############################################
# 9. Done
###############################################
info "============================================"
info "DEPLOY ЗАВЕРШЁН"
info "Admin login: $ADMIN_USER"
info "Admin pass:  $ADMIN_PASS"
info "Admin email: $ADMIN_EMAIL"
info "Container web: $WEB_CONTAINER"
info "============================================"
