#!/bin/bash

set -o allexport
source ./backend/.env
set +o allexport

# Настройки
# NEXUS_REGISTRY_URL="localhost:5000"
# NEXUS_REGISTRY_URL="192.168.49.2:5000"
echo "NEXUS_WEB_URL: $NEXUS_WEB_URL"
 
TAG=${1:-latest}
# NEXUS_USER="admin"
# NEXUS_PASS="superpass123"

echo "Используем тег: $TAG"

# Проверка доступности Nexus
echo "Проверка доступности Nexus..."
if ! curl -s --head $NEXUS_WEB_URL > /dev/null; then
    echo "❌ Nexus не доступен на $NEXUS_WEB_URL"
    echo "Запустите Nexus: docker compose up -d nexus"
    exit 1
fi

# Проверка доступа к Docker реестру Nexus
echo "Проверка Docker реестра Nexus..."
if ! curl -s --head $NEXUS_REGISTRY_URL > /dev/null; then
    echo "❌ Docker реестр Nexus не доступен на $NEXUS_REGISTRY_URL"
    exit 1
fi

echo "Логин в Nexus..."
echo $NEXUS_PASSWORD | docker login -u $NEXUS_USER --password-stdin $NEXUS_REGISTRY_URL
# echo $NEXUS_PASSWORD  $NEXUS_USER  $NEXUS_REGISTRY_URL

if [ $? -ne 0 ]; then
    echo "❌ Ошибка логина в Nexus"
    echo "Проверьте:"
    echo "1. Правильность пароля"
    echo "2. Аутентификацию в Nexus (Settings > Security > Anonymous Access)"
    exit 1
fi

echo "✅ Успешный логин в Nexus"

# Аргументы сборки для каждого сервиса
# FIX http
declare -A BUILD_ARGS=(
    ["admin-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local/api/admin --build-arg SVELTEKIT_BASEPATH='/admin'" 
    ["order-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local/api/order --build-arg SVELTEKIT_BASEPATH='/order'" 
    ["courier-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local/api/courier --build-arg SVELTEKIT_BASEPATH='/courier' --build-arg WEB_SOCKET_URL=ws://healthy-menu.local/api/courier"
    ["admin-backend"]=""
    ["order-backend"]=""
    ["courier-backend"]=""
)

# Все сервисы с путями
declare -a SERVICES=(
    "admin-frontend   ./frontend/admin-healthy-menu"
    "order-frontend   ./frontend/order-healthy-menu"
    "courier-frontend ./frontend/courier-healthy-menu"
    "admin-backend    ./backend ./backend/admin/Dockerfile"
    "order-backend    ./backend ./backend/order/Dockerfile"
    "courier-backend  ./backend ./backend/courier/Dockerfile"
)

echo "🚀 Publishing to $NEXUS_REGISTRY_URL"  # Исправлено: было $EGISTRY
echo "============================="

success=0
fail=0

# Функция для очистки при прерывании
cleanup() {
    echo ""
    echo "Прерывание операции..."
    docker logout $NEXUS_REGISTRY_URL
    exit 1
}
trap cleanup INT TERM

for item in "${SERVICES[@]}"; do
    read -r name context dockerfile <<< "$item"
    
    echo "=== $name ==="
    
    # Если dockerfile не указан, используем стандартный
    if [ -z "$dockerfile" ]; then
        dockerfile="$context/Dockerfile"
    fi
    
    # Проверяем существование файлов
    if [ ! -d "$context" ]; then
        echo "❌ Context directory not found: $context"
        ((fail++))
        continue
    fi
    
    if [ ! -f "$dockerfile" ]; then
        echo "❌ Dockerfile not found: $dockerfile"
        ((fail++))
        continue
    fi
    
    # Получаем аргументы сборки для этого сервиса
    ARGS="${BUILD_ARGS[$name]}"
    
    # Формируем и выполняем команду сборки
    BUILD_CMD="docker build $ARGS -t $NEXUS_REGISTRY_URL/$name:$TAG -f $dockerfile $context"
    
    echo "\$ $BUILD_CMD"
    # Сборка
    if eval "$BUILD_CMD"; then  # Убрал > /dev/null 2>&1 для отладки
        echo "  ✅ Built"
    else
        echo "❌ Build failed"
        ((fail++))
        continue
    fi
    
    # Проверяем, что образ создался
    if ! docker image inspect "$NEXUS_REGISTRY_URL/$name:$TAG" &> /dev/null; then
        echo "❌ Образ не найден после сборки: $NEXUS_REGISTRY_URL/$name:$TAG"
        ((fail++))
        continue
    fi
    
    # Публикация
    PUBLISH_CMD="docker push $NEXUS_REGISTRY_URL/$name:$TAG"
    echo "\$ $PUBLISH_CMD"
    if eval "$PUBLISH_CMD"; then  # Убрал > /dev/null 2>&1 для отладки
        echo "  ✅ Published"
        ((success++))
    else
        echo "❌ Push failed"
        echo "Возможные причины:"
        echo "1. Docker не настроен на работу с insecure registry"
        echo "2. Nexus не разрешает push в репозиторий"
        echo "3. Проблемы с сетью"
        ((fail++))
    fi
    
    echo ""
done

docker logout $NEXUS_REGISTRY_URL

echo "======================================="
echo "📊 Results: $success published, $fail failed"
echo "======================================="

if [ $fail -eq 0 ]; then
    echo "🎉 Success!"
else
    echo "⚠️  Some images failed to publish"
    exit 1
fi





