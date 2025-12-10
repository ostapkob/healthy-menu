#!/bin/bash

REGISTRY="192.168.49.2:5000"
TAG="latest"

# Аргументы сборки для каждого сервиса
declare -A BUILD_ARGS=(
    ["admin-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local/api/admin --build-arg SVELTEKIT_BASEPATH='/admin'"
    ["order-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local/api/order --build-arg SVELTEKIT_BASEPATH='/order'" 
    ["courier-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local/api/courier --build-arg SVELTEKIT_BASEPATH='/courier' --build-arg VITE_WEB_SOCKET_URL=ws://healthy-menu.local/api/courier"
    ["admin-backend"]=""
    ["order-backend"]=""
    ["courier-backend"]=""
    ["nginx-proxy"]=""
)

# Все сервисы с путями
declare -a SERVICES=(
    "admin-frontend   ./frontend/admin-healthy-menu"
    "order-frontend   ./frontend/order-healthy-menu"
    "courier-frontend ./frontend/courier-healthy-menu"
    "admin-backend    ./backend ./backend/admin/Dockerfile"
    "order-backend    ./backend ./backend/order/Dockerfile"
    "courier-backend  ./backend ./backend/courier/Dockerfile"
    "nginx-proxy      ./frontend/nginx-proxy"
)

echo "🚀 Publishing to $REGISTRY"
echo "============================="

success=0
fail=0

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
    BUILD_CMD="docker build $ARGS -t $REGISTRY/$name:$TAG -f $dockerfile $context"
    
    echo "\$ $BUILD_CMD"
    # Сборка
    if eval "$BUILD_CMD" > /dev/null 2>&1; then
        echo "  ✅ Built"
    else
        echo "❌ Build failed"
        ((fail++))
        continue
    fi
    
    # Публикация
    PUBLISH_CMD="docker push $REGISTRY/$name:$TAG"
    if eval "$PUBLISH_CMD" > /dev/null 2>&1; then
        echo "\$ $PUBLISH_CMD"
        echo "  ✅ Published"
        ((success++))
    else
        echo "❌ Push failed"
        ((fail++))
    fi
    
    echo ""
done

echo "======================================="
echo "📊 Results: $success published, $fail failed"
echo "======================================="

if [ $fail -eq 0 ]; then
    echo "🎉 Success!"
else
    echo "⚠️  Some images failed to publish"
    exit 1
fi
