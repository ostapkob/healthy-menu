#!/bin/bash

REGISTRY="192.168.49.2:5000"
TAG="latest"

echo "🚀 Publishing to $REGISTRY"
echo "============================="

# Функция для обработки ошибок
handle_error() {
    echo "❌ Error at line $1"
    echo "Continuing with next service..."
}

trap 'handle_error $LINENO' ERR

# Массив сервисов с правильными путями
services=(
    "admin-frontend   ./frontend/admin-healthy-menu"
    "order-frontend   ./frontend/order-healthy-menu"
    "courier-frontend ./frontend/courier-healthy-menu"
    "admin-backend ./backend ./backend/admin/Dockerfile"
    "order-backend ./backend ./backend/order/Dockerfile"
    "courier-backend ./backend ./backend/courier/Dockerfile"
    "nginx-proxy ./frontend/nginx-proxy"
)

success=0
fail=0

for item in "${services[@]}"; do
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
        echo "  Looking for Dockerfile in $context..."
        find "$context" -name "Dockerfile" -type f 2>/dev/null | head -2
        ((fail++))
        continue
    fi
    
    echo "  Context: $context"
    echo "  Dockerfile: $dockerfile"
    
    # Сборка
    echo "  Building..."
    if docker build -t "$REGISTRY/$name:$TAG" -f "$dockerfile" "$context" 2>/dev/null; then
        echo "  ✅ Built"
    else
        echo "❌ Build failed"
        ((fail++))
        continue
    fi
    
    # Публикация
    echo "  Pushing..."
    if docker push "$REGISTRY/$name:$TAG" 2>/dev/null; then
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
    echo "⚠️  Check the errors above"
    exit 1
fi
