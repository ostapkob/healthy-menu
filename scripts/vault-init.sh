#!/bin/bash
#
# Скрипт инициализации HashiCorp Vault
# Загружает секреты из .env файла в Vault
#

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Переменные
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-vault-root-token}"
ENV_FILE="${1:-./.env}"

# Экспорт переменных окружения
export VAULT_ADDR
export VAULT_TOKEN

echo -e "${BLUE}╔════════════════════════════════════════╗"
echo -e "║  HashiCorp Vault Initialization Script ║"
echo -e "╚════════════════════════════════════════╝${NC}"
echo ""

# Проверка .env файла
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Файл $ENV_FILE не найден${NC}"
    exit 1
fi

echo -e "${GREEN}📄 Загрузка переменных из $ENV_FILE${NC}"

# Загрузка переменных из .env
set -a
source "$ENV_FILE"
set +a

# Проверка доступности Vault
echo -e "${GREEN}⏳ Проверка доступности Vault...${NC}"
max_wait=60
counter=0

until vault status >/dev/null 2>&1; do
    if [ $counter -ge $max_wait ]; then
        echo -e "${RED}❌ Vault не доступен после ${max_wait} секунд${NC}"
        echo -e "${YELLOW}💡 Убедись, что Vault запущен:${NC}"
        echo -e "   ${BLUE}docker ps | grep vault${NC}"
        exit 1
    fi
    echo -e "${YELLOW}   Ожидание Vault... (${counter}s)${NC}"
    sleep 2
    counter=$((counter + 2))
done

echo -e "${GREEN}✅ Vault доступен${NC}"
echo ""

# Включение KV secrets engine v2
echo -e "${GREEN}📦 Включение KV secrets engine v2...${NC}"
if vault secrets enable -path=secret kv-v2 2>/dev/null; then
    echo -e "${GREEN}   ✅ KV engine включён${NC}"
else
    echo -e "${YELLOW}   ⚠️  KV engine уже включён${NC}"
fi
echo ""

# Создание секретов
echo -e "${GREEN}🔑 Создание секретов...${NC}"
echo ""

# PostgreSQL
echo -e "${BLUE}  📦 PostgreSQL${NC}"
vault kv put secret/postgres \
    username="${POSTGRES_USER}" \
    password="${POSTGRES_PASSWORD}" \
    database="${POSTGRES_DB}" \
    host="${POSTGRES_HOST:-postgres}" \
    port="${POSTGRES_PORT:-5432}" \
    connection_url="${POSTGRES_DATABASE_URL}" \
    test_url="${POSTGRES_DATABASE_TEST_URL:-}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# MinIO
echo -e "${BLUE}  📦 MinIO${NC}"
vault kv put secret/minio \
    root_user="${MINIO_ROOT_USER}" \
    root_password="${MINIO_ROOT_PASSWORD}" \
    bucket="${MINIO_BUCKET}" \
    host="${MINIO_HOST:-minio}" \
    port="${MINIO_PORT:-9000}" \
    url="${MINIO_URL:-http://$MINIO_HOST:$MINIO_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Kafka
echo -e "${BLUE}  📦 Kafka${NC}"
vault kv put secret/kafka \
    bootstrap_servers="${KAFKA_BOOTSTRAP_SERVERS}" \
    advertised_listeners="${KAFKA_ADVERTISED_LISTENERS}" \
    zookeeper_connect="${KAFKA_ZOOKEEPER_CONNECT:-zookeeper:2181}" \
    topics="new_orders,orders,events,notifications" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Nexus
echo -e "${BLUE}  📦 Nexus${NC}"
vault kv put secret/nexus \
    host="${NEXUS_HOST:-nexus}" \
    port="${NEXUS_PORT:-8081}" \
    registry_port="${NEXUS_REGISTRY_PORT:-5000}" \
    username="${NEXUS_USER_NAME}" \
    password="${NEXUS_USER_PASSWORD}" \
    admin_password="${NEXUS_ADMIN_NEW_PASS}" \
    url="${NEXUS_URL:-http://$NEXUS_HOST:$NEXUS_PORT}" \
    registry_url="${NEXUS_HOST}:${NEXUS_REGISTRY_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# GitLab
echo -e "${BLUE}  📦 GitLab${NC}"
vault kv put secret/gitlab \
    host="${GITLAB_HOST:-gitlab}" \
    port="${GITLAB_PORT:-8060}" \
    root_password="${GITLAB_ROOT_PASSWORD}" \
    root_token="${GITLAB_ROOT_TOKEN}" \
    access_token="${GITLAB_ACCESS_TOKEN}" \
    user="${GITLAB_USER}" \
    user_password="${GITLAB_PASSWORD}" \
    url="${GITLAB_URL:-http://$GITLAB_HOST:$GITLAB_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# SonarQube
echo -e "${BLUE}  📦 SonarQube${NC}"
vault kv put secret/sonarqube \
    host="${SONAR_HOST:-sonarqube}" \
    port="${SONAR_PORT:-9000}" \
    admin_password="${SONAR_ADMIN_NEW_PASS:-admin}" \
    admin_token="${SONAR_ADMIN_TOKEN}" \
    user_token="${SONAR_USER_TOKEN}" \
    jdbc_url="${SONAR_JDBC_URL}" \
    jdbc_user="${SONAR_JDBC_USERNAME}" \
    jdbc_password="${SONAR_JDBC_PASSWORD}" \
    webhook_url="${SONAR_JENKINS_WEBHOOK_URL}" \
    url="${SONAR_URL:-http://$SONAR_HOST:$SONAR_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Jenkins
echo -e "${BLUE}  📦 Jenkins${NC}"
vault kv put secret/jenkins \
    host="${JENKINS_HOST:-jenkins}" \
    port="${JENKINS_PORT:-8080}" \
    secret="${JENKINS_SECRET}" \
    agent_name="${JENKINS_AGENT_NAME}" \
    agent_workdir="${JENKINS_AGENT_WORKDIR}" \
    url="${JENKINS_URL:-http://$JENKINS_HOST:$JENKINS_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# ArgoCD
echo -e "${BLUE}  📦 ArgoCD${NC}"
vault kv put secret/argocd \
    password="${ARGO_PASSWORD}" \
    admin_username="admin" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# JWT (генерируем случайный ключ если не задан)
echo -e "${BLUE}  📦 JWT${NC}"
JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32)}"
vault kv put secret/jwt \
    secret_key="$JWT_SECRET" \
    algorithm="HS256" \
    expiration="3600" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗"
echo -e "║  ✅  Инициализация завершена!          ║"
echo -e "╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📊 Vault UI:${NC} http://localhost:8200"
echo -e "${BLUE}🔑 Token:${NC} $VAULT_TOKEN"
echo ""
echo -e "${BLUE}📝 Примеры использования:${NC}"
echo -e "  ${YELLOW}# Получить секрет:${NC}"
echo -e "  vault kv get secret/postgres"
echo ""
echo -e "  ${YELLOW}# Использовать в приложении:${NC}"
echo -e "  export VAULT_ADDR=$VAULT_ADDR"
echo -e "  export VAULT_TOKEN=$VAULT_TOKEN"
echo -e "  vault kv get secret/postgres"
echo ""
echo -e "  ${YELLOW}# Экспорт переменных:${NC}"
echo -e "  eval \"\$(vault kv get -format=json secret/postgres | jq -r '.data.data | to_entries | .[] | \"export \\(.key | ascii_upcase)=\\(.value)\"')\""
echo ""
