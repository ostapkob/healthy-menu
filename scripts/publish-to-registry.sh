#!/bin/bash

set -o allexport
source ./.env
set +o allexport

NEXUS_WEB_URL=$NEXUS_HOST:$NEXUS_PORT
TAG=${1:-latest}

echo "🚀 Реестр: $NEXUS_REGISTRY_URL | Тег: $TAG"

# Проверка Nexus
if ! curl -s --head --connect-timeout 5 "$NEXUS_WEB_URL" > /dev/null; then
    echo "❌ Nexus не доступен на $NEXUS_WEB_URL"
    exit 1
fi

echo "🔐 Логин в Nexus..."
echo "$NEXUS_USER_PASSWORD" | docker login -u "$NEXUS_USER_NAME" --password-stdin "$NEXUS_REGISTRY_URL" || exit 1

# Аргументы сборки
declare -A BUILD_ARGS=(
    ["admin-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local --build-arg SVELTEKIT_BASEPATH=/admin" 
    ["order-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local --build-arg SVELTEKIT_BASEPATH=/order" 
    ["courier-frontend"]="--build-arg API_BASE_URL=http://healthy-menu.local --build-arg SVELTEKIT_BASEPATH=/courier --build-arg WEB_SOCKET_URL=ws://healthy-menu.local/api/courier"
)

# Все сервисы теперь ищутся в одноименных папках
declare -a SERVICES=(
    "admin-frontend"
    "order-frontend"
    "courier-frontend"
    "admin-backend"
    "order-backend"
    "courier-backend"
)

success=0
fail=0

trap 'docker logout $NEXUS_REGISTRY_URL; exit 1' INT TERM

for name in "${SERVICES[@]}"; do
    context="./$name"
    dockerfile="$context/Dockerfile"
    full_image="$NEXUS_REGISTRY_URL/$name:$TAG"
    args=${BUILD_ARGS[$name]}

    echo "=== [ $name ] ==="

    if [ ! -f "$dockerfile" ]; then
        echo "❌ Ошибка: Файл $dockerfile не найден"
        ((fail++))
        continue
    fi

    # Вывод и выполнение команды сборки
    echo "📦 Подготовка сборки..."
    
    build_params=($args) 
    
    echo "$ docker build ${build_params[@]} -t $full_image -f $dockerfile $context"
    
    if docker build "${build_params[@]}" -t "$full_image" -f "$dockerfile" "$context"; then
        echo "✅ Сборка OK"
    else
        echo "❌ Ошибка сборки"
        ((fail++))
        continue
    fi

    # Вывод и выполнение команды отправки
    echo "🚀 Отправка в реестр..."
    echo "$ docker push $full_image"
    
    if docker push "$full_image"; then
        echo "✅ Опубликовано"
        ((success++))
    else
        echo "❌ Ошибка push"
        ((fail++))
    fi
    echo ""
done

docker logout "$NEXUS_REGISTRY_URL"

echo "======================================="
echo "📊 Итог: $success ок, $fail ошибок"
echo "======================================="

[ $fail -eq 0 ] || exit 1

