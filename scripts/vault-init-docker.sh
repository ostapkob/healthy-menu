#!/bin/bash
#
# Скрипт инициализации HashiCorp Vault внутри контейнера
# Запускает vault-init.sh внутри контейнера Vault
#

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ENV_FILE="${1:-./.env}"
CONTAINER_NAME="vault"

echo -e "${BLUE}╔════════════════════════════════════════╗"
echo -e "║     Vault Init (inside container)         ║"
echo -e "╚════════════════════════════════════════╝${NC}"
echo ""

# Проверка контейнера
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo -e "${RED}❌ Контейнер $CONTAINER_NAME не найден${NC}"
    echo -e "${YELLOW}💡 Запусти Vault:${NC}"
    echo -e "   ${BLUE}docker start vault${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Контейнер найден: $CONTAINER_NAME${NC}"

# Проверка .env файла
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Файл $ENV_FILE не найден${NC}"
    exit 1
fi

echo -e "${GREEN}📄 Копирование .env в контейнер...${NC}"

# Копирование .env во временную папку
TEMP_ENV="/tmp/vault-env-$(date +%s)"
docker cp "$ENV_FILE" "$CONTAINER_NAME:$TEMP_ENV"

echo -e "${GREEN}🚀 Запуск инициализации в контейнере...${NC}"
echo ""

# Запуск скрипта внутри контейнера
docker exec -it "$CONTAINER_NAME" bash -c "
    export VAULT_ADDR='http://localhost:8200'
    export VAULT_TOKEN='vault-root-token'
    
    # Ждём Vault
    echo '⏳ Ожидание Vault...'
    until vault status >/dev/null 2>&1; do
        sleep 2
    done
    
    # Включение KV engine
    echo '📦 Включение KV engine...'
    vault secrets enable -path=secret kv-v2 2>/dev/null || echo 'KV engine уже включён'
    
    # Загрузка переменных
    set -a
    source $TEMP_ENV
    set +a
    
    # Создание секретов
    echo ''
    echo '🔑 Создание секретов...'
    echo ''
    
    # PostgreSQL
    echo '  📦 PostgreSQL'
    vault kv put secret/postgres \\
        username=\"\$POSTGRES_USER\" \\
        password=\"\$POSTGRES_PASSWORD\" \\
        database=\"\$POSTGRES_DB\" \\
        host=\"\${POSTGRES_HOST:-postgres}\" \\
        port=\"\${POSTGRES_PORT:-5432}\" \\
        connection_url=\"\$POSTGRES_DATABASE_URL\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # MinIO
    echo '  📦 MinIO'
    vault kv put secret/minio \\
        root_user=\"\$MINIO_ROOT_USER\" \\
        root_password=\"\$MINIO_ROOT_PASSWORD\" \\
        bucket=\"\$MINIO_BUCKET\" \\
        host=\"\${MINIO_HOST:-minio}\" \\
        port=\"\${MINIO_PORT:-9000}\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # Kafka
    echo '  📦 Kafka'
    vault kv put secret/kafka \\
        bootstrap_servers=\"\$KAFKA_BOOTSTRAP_SERVERS\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # Nexus
    echo '  📦 Nexus'
    vault kv put secret/nexus \\
        host=\"\${NEXUS_HOST:-nexus}\" \\
        port=\"\${NEXUS_PORT:-8081}\" \\
        username=\"\$NEXUS_USER_NAME\" \\
        password=\"\$NEXUS_USER_PASSWORD\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # GitLab
    echo '  📦 GitLab'
    vault kv put secret/gitlab \\
        host=\"\${GITLAB_HOST:-gitlab}\" \\
        port=\"\${GITLAB_PORT:-8060}\" \\
        root_token=\"\$GITLAB_ROOT_TOKEN\" \\
        access_token=\"\$GITLAB_ACCESS_TOKEN\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # SonarQube
    echo '  📦 SonarQube'
    vault kv put secret/sonarqube \\
        host=\"\${SONAR_HOST:-sonarqube}\" \\
        port=\"\${SONAR_PORT:-9000}\" \\
        admin_token=\"\$SONAR_ADMIN_TOKEN\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # Jenkins
    echo '  📦 Jenkins'
    vault kv put secret/jenkins \\
        host=\"\${JENKINS_HOST:-jenkins}\" \\
        port=\"\${JENKINS_PORT:-8080}\" \\
        secret=\"\$JENKINS_SECRET\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # ArgoCD
    echo '  📦 ArgoCD'
    vault kv put secret/argocd \\
        password=\"\$ARGO_PASSWORD\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    # JWT
    echo '  📦 JWT'
    vault kv put secret/jwt \\
        secret_key=\"vault-jwt-secret-key\" \\
        algorithm=\"HS256\" \\
        expiration=\"3600\" 2>/dev/null && \\
        echo '     ✅' || echo '     ⚠️'
    
    echo ''
    echo '✅ Инициализация завершена!'
    
    # Очистка
    rm -f $TEMP_ENV
"

echo ""
echo -e "${GREEN}✅ Готово!${NC}"
echo ""
echo -e "${BLUE}📝 Примеры использования:${NC}"
echo -e "  ${YELLOW}# Получить секрет через docker exec:${NC}"
echo -e "  docker exec -it vault vault kv get secret/postgres"
echo ""
echo -e "  ${YELLOW}# Или через HTTP API:${NC}"
echo -e "  curl -H \"X-Vault-Token: vault-root-token\" \\
    http://localhost:8200/v1/secret/data/postgres"
echo ""
