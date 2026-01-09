#!/bin/bash
# 
set -o allexport
source ./backend/.env
set +o allexport

# Получаем пароль администратора
ADMIN_PASSWORD=$(docker exec nexus cat /nexus-data/admin.password)
# NEXUS_WEB_HOST="http://localhost:8081"

echo "Пароль администратора: $ADMIN_PASSWORD"

# Включаем Docker Bearer Token Realm
echo "Включение Docker Bearer Token Realm..."


# Задаем список активных realms, включая DockerToken
curl -u "admin:$ADMIN_PASSWORD" -X PUT \
  "$NEXUS_WEB_URL/service/rest/v1/security/realms/active" \
  -H "Content-Type: application/json" \
  -H 'accept: application/json' \
  -H 'X-Nexus-UI: true' \
  -d '[
    "NexusAuthenticatingRealm",
    "DockerToken"
  ]'


# Получаем текущие активные realms
curl -s -u "admin:$ADMIN_PASSWORD" \
  "$NEXUS_WEB_URL/service/rest/v1/security/realms/active"
  

# Настройка репозитория Docker hosted
curl -u "admin:$ADMIN_PASSWORD" -X POST \
  "$NEXUS_WEB_URL/service/rest/v1/repositories/docker/hosted" \
  -H "Content-Type: application/json" \
  -d '{
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
      "httpPort": '"$NEXUS_PORT"'
    }
  }'

# Смена пароля администратора
echo ""
echo "Смена пароля администратора..."
curl -u "admin:$ADMIN_PASSWORD" -X PUT \
  "$NEXUS_WEB_URL/service/rest/v1/security/users/admin/change-password" \
  -H "Content-Type: text/plain" \
  -d "$NEXUS_URL"

echo "Войдите в web итерфейс, после этого можно будет залогинится коммандой"
echo "docker login localhost:5000 -u admin"
