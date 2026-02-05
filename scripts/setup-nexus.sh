#!/bin/bash
set -e

set -o allexport
source ./.env
set +o allexport

echo "🔧 Nexus Configuration Script"
echo "============================="

# Параметры
echo "Parameters:"
echo "  URL: ${NEXUS__URL}"
echo "  Admin new password: [set]"
echo "  User: ${NEXUS_USER_NAME}"
echo "  User password: [set]"

# Функция для ожидания
wait_for_nexus() {
    echo "⏳ Waiting for Nexus to start (max 5 minutes)..."

    local max_wait=300
    local counter=0
 
    while true; do
        if curl -s --fail $NEXUS_WEB_URL > /dev/null; then
            echo "✅ Nexus is responding!"
            return 0
        fi

        sleep 5
        counter=$((counter + 5))
        echo "   Waited ${counter}s..."

        if [ $counter -ge $max_wait ]; then
            echo "❌ Nexus did not start in ${max_wait} seconds"
            return 1
        fi
    done
}

# Функция для выполнения API-запросов
nexus_api() {
    local username="$1"
    local password="$2"
    local method="$3"
    local endpoint="$4"
    local data="$5"
    
    local curl_cmd="curl -s -w 'HTTP_STATUS:%{http_code}' -f -u '${username}:${password}' \
        -X '${method}' \
        '${NEXUS_URL}${endpoint}' \
        -H 'Content-Type: application/json' \
        -H 'accept: application/json'"
    
    if [ -n "$data" ]; then
        curl_cmd="${curl_cmd} --data '${data}'"
    fi
    
    echo "   [API] ${method} ${endpoint}"
    
    # Выполняем запрос
    response=$(eval "$curl_cmd" 2>/dev/null || echo "HTTP_STATUS:000")
    
    # Извлекаем статус
    http_status=$(echo "$response" | grep -o 'HTTP_STATUS:[0-9]*' | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*//')
    
    if [ "$http_status" -ge 200 ] && [ "$http_status" -lt 300 ]; then
        echo "   ✅ Success (HTTP ${http_status})"
        return 0
    else
        echo "   ⚠️  Failed (HTTP ${http_status})"
        [ -n "$body" ] && echo "   Response: ${body:0:200}..."
        return 1
    fi
}

# Ожидаем запуск Nexus
wait_for_nexus

# Получаем начальный пароль
echo ""
echo "🔑 Getting initial admin password..."
INITIAL_PASS=$(docker exec nexus cat /nexus-data/admin.password 2>/dev/null || echo "")

if [ -z "$INITIAL_PASS" ]; then
    echo "⚠️  Nexus already configured or no initial password found"
    echo "   Trying to authenticate with provided password..."
    
    # Пробуем аутентифицироваться с новым паролем
    if curl -s -u "admin:${NEXUS_ADMIN_NEW_PASS}" "${NEXUS_URL}/service/rest/v1/status" > /dev/null; then
        echo "✅ Nexus already configured with new password"
        INITIAL_PASS="$NEXUS_ADMIN_NEW_PASS"
    else
        echo "❌ Cannot authenticate. Nexus might be in unexpected state."
        echo "   Try: docker exec nexus cat /nexus-data/admin.password"
        exit 1
    fi
else
    echo "📝 Initial password: ${INITIAL_PASS}"
fi

echo ""
echo "🔧 Starting configuration..."

# 1. Включаем Docker Bearer Token Realm
echo "1. Enabling Docker Bearer Token Realm..."
nexus_api "admin" "$INITIAL_PASS" "PUT" "/service/rest/v1/security/realms/active" '[
  "NexusAuthenticatingRealm",
  "DockerToken"
]' || echo "   ℹ️  May already be configured"

# 2. Создаём Docker hosted репозиторий
echo ""
echo "2. Creating Docker hosted repository..."
nexus_api "admin" "$INITIAL_PASS" "POST" "/service/rest/v1/repositories/docker/hosted" '{
  "name": "docker-hosted",
  "online": true,
  "storage": {
    "blobStoreName": "default",
    "strictContentTypeValidation": true,
    "writePolicy": "allow_once"
  },
  "docker": {
    "v1Enabled": false,
    "forceBasicAuth": false,
    "httpPort": 5000
  }
}' || echo "   ℹ️  May already exist"

# 3. Создаём Helm hosted репозиторий
echo ""
echo "3. Creating Helm hosted repository..."
nexus_api "admin" "$INITIAL_PASS" "POST" "/service/rest/v1/repositories/helm/hosted" '{
  "name": "helm-hosted",
  "online": true,
  "storage": {
    "blobStoreName": "default",
    "strictContentTypeValidation": true,
    "writePolicy": "allow_once"
  }
}' || echo "   ℹ️  May already exist"

# 4. Меняем пароль администратора (только если у нас начальный пароль)
if [ "$INITIAL_PASS" != "$NEXUS_ADMIN_NEW_PASS" ]; then
    echo ""
    echo "4. Changing admin password..."
    
    if curl -s -u "admin:${INITIAL_PASS}" \
        -X PUT \
        "${NEXUS_URL}/service/rest/v1/security/users/admin/change-password" \
        -H "Content-Type: text/plain" \
        --data "${NEXUS_ADMIN_NEW_PASS}" > /dev/null 2>&1; then
        echo "   ✅ Admin password changed"
        
        # Ждём применения пароля
        sleep 2
        
        # Проверяем новый пароль
        if curl -s -u "admin:${NEXUS_ADMIN_NEW_PASS}" "${NEXUS_URL}/service/rest/v1/status" > /dev/null; then
            echo "   ✅ New password verified"
            CURRENT_ADMIN_PASS="$NEXUS_ADMIN_NEW_PASS"
        else
            echo "   ⚠️  New password might not work"
            CURRENT_ADMIN_PASS="$INITIAL_PASS"
        fi
    else
        echo "   ⚠️  Failed to change password"
        CURRENT_ADMIN_PASS="$INITIAL_PASS"
    fi
else
    echo ""
    echo "4. Admin password already changed"
    CURRENT_ADMIN_PASS="$NEXUS_ADMIN_NEW_PASS"
fi

# 5. Создаём дополнительного пользователя
echo ""
echo "5. Creating user '${NEXUS_USER_NAME}'..."
nexus_api "admin" "$CURRENT_ADMIN_PASS" "POST" "/service/rest/v1/security/users" "{
  \"userId\": \"${NEXUS_USER_NAME}\",
  \"firstName\": \"Terraform\",
  \"lastName\": \"User\",
  \"emailAddress\": \"${NEXUS_USER_NAME}@example.com\",
  \"password\": \"${NEXUS_USER_PASSWORD}\",
  \"status\": \"active\",
  \"roles\": [\"nx-admin\"]
}" || echo "   ℹ️  User may already exist"

# 6. Проверяем создание пользователя
echo ""
echo "6. Verifying configuration..."
if curl -s -u "admin:${CURRENT_ADMIN_PASS}" \
    "${NEXUS_URL}/service/rest/v1/security/users" \
    | grep "userId" | grep  ${NEXUS_USER_NAME} > /dev/null 2>&1; then
    echo "   ✅ User '${NEXUS_USER_NAME}' confirmed"
else
    echo "   ⚠️  User '${NEXUS_USER_NAME}' not found"
    echo "   Debug: first 200 chars of response:"
    curl -s -u "admin:${CURRENT_ADMIN_PASS}" "${NEXUS_URL}/service/rest/v1/security/users" | head -c 200
fi

echo ""
echo "========================================="
echo "🎉 Nexus configuration script complete!"
echo ""
echo "📊 Nexus UI:   $NEXUS_WEB_URL"
echo "👤 Admin:      admin / ${NEXUS_ADMIN_NEW_PASS}"
echo "👤 User:       ${NEXUS_USER_NAME} / ${NEXUS_USER_PASSWORD}"
echo "🐳 Registry:   localhost:5000"
echo ""
echo "Test commands:"
echo "  curl -u admin:${NEXUS_ADMIN_NEW_PASS} ${NEXUS_URL}/service/rest/v1/status"
echo "  docker login localhost:5000 -u admin"
echo "========================================="

# Создаём маркерный файл
# echo "nexus_configured: true" > /tmp/nexus_configured.txt
# echo "admin: admin / ${NEXUS_ADMIN_NEW_PASS}" >> /tmp/nexus_configured.txt
# echo "user: ${USER_NAME} / ${NEXUS_USER_PASSWORD}" >> /tmp/nexus_configured.txt
# echo "timestamp: $(date)" >> /tmp/nexus_configured.txt
