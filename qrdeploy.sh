#!/bin/bash

# ------------------------------------------------------
# QR Project Auto-Deploy Script
# ------------------------------------------------------

# Настройки
PROJECT_NAME="Esschert_Design_QR_generator"
GITHUB_REPO="https://github.com/yourusername/yourrepo.git"
PROJECT_DIR="/opt/$PROJECT_NAME"
ENV_FILE=".env"

# Функция для вывода сообщений
info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
    exit 1
}

# ------------------------------------------------------
# Проверка и установка Docker
# ------------------------------------------------------
if ! command -v docker &> /dev/null; then
    info "Docker не найден. Устанавливаем..."
    sudo apt update
    sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    sudo systemctl enable docker
    sudo systemctl start docker
else
    info "Docker уже установлен"
fi

# Проверка docker-compose
if ! command -v docker-compose &> /dev/null; then
    info "docker-compose не найден. Устанавливаем..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    info "docker-compose уже установлен"
fi

# ------------------------------------------------------
# Проверка MySQL 8
# ------------------------------------------------------
if ! command -v mysql &> /dev/null; then
    info "MySQL не найден. Устанавливаем MySQL 8..."
    sudo apt update
    sudo apt install -y mysql-server
    sudo systemctl enable mysql
    sudo systemctl start mysql
else
    MYSQL_VERSION=$(mysql --version | awk '{print $5}' | sed 's/,//')
    info "MySQL уже установлен: $MYSQL_VERSION"
fi

# ------------------------------------------------------
# Клонирование или обновление репозитория
# ------------------------------------------------------
if [ -d "$PROJECT_DIR" ]; then
    info "Проект уже существует. Обновляем..."
    cd "$PROJECT_DIR" || error "Не удалось зайти в папку проекта"
    git reset --hard
    git pull origin main
else
    info "Клонируем проект с GitHub..."
    sudo git clone "$GITHUB_REPO" "$PROJECT_DIR" || error "Не удалось клонировать репозиторий"
    cd "$PROJECT_DIR" || error "Не удалось зайти в папку проекта"
fi

# ------------------------------------------------------
# Копирование .env
# ------------------------------------------------------
if [ -f "$ENV_FILE" ]; then
    info "Копируем .env файл..."
    cp "$ENV_FILE" "$PROJECT_DIR/.env"
else
    error ".env файл не найден!"
fi

# ------------------------------------------------------
# Сборка и запуск Docker
# ------------------------------------------------------
info "Собираем Docker-контейнеры..."
sudo docker-compose build --no-cache || error "Ошибка сборки Docker"

info "Запускаем Docker-контейнеры..."
sudo docker-compose up -d || error "Ошибка запуска Docker"

info "Деплой завершён успешно!"
