#!/bin/bash
#
# Скрипт полной инициализации HashiCorp Vault
# - Загружает секреты из .env файла
# - Создаёт policies для доступа к секретам
# - Настраивает Kubernetes auth method и роли
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

echo -e "${BLUE}╔════════════════════════════════════════════════╗"
echo -e "║     HashiCorp Vault Full Initialization        ║"
echo -e "╚════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Проверка .env файла и загрузка переменных
# =============================================================================

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ Файл $ENV_FILE не найден${NC}"
    exit 1
fi

echo -e "${GREEN}📄 Загрузка переменных из $ENV_FILE${NC}"

set -a
source "$ENV_FILE"
set +a

# =============================================================================
# Проверка доступности Vault
# =============================================================================

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

# =============================================================================
# Включение KV secrets engine v2
# =============================================================================

echo -e "${GREEN}📦 Включение KV secrets engine v2...${NC}"
if vault secrets enable -path=secret kv-v2 2>/dev/null; then
    echo -e "${GREEN}   ✅ KV engine включён${NC}"
else
    echo -e "${YELLOW}   ⚠️  KV engine уже включён${NC}"
fi
echo ""

# =============================================================================
# Создание секретов из .env файла
# =============================================================================

echo -e "${GREEN}🔑 Создание секретов...${NC}"
echo ""

# PostgreSQL
echo -e "${BLUE}  📦 PostgreSQL${NC}"
vault kv put secret/postgres \
    POSTGRES_USER="${POSTGRES_USER}" \
    POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    POSTGRES_DB="${POSTGRES_DB}" \
    POSTGRES_HOST="${POSTGRES_HOST:-postgres}" \
    POSTGRES_PORT="${POSTGRES_PORT:-5432}" \
    POSTGRES_DATABASE_URL="${POSTGRES_DATABASE_URL}" \
    POSTGRES_DATABASE_TEST_URL="${POSTGRES_DATABASE_TEST_URL:-}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# MinIO
echo -e "${BLUE}  📦 MinIO${NC}"
vault kv put secret/minio \
    MINIO_HOST="${MINIO_HOST:-minio}" \
    MINIO_PORT="${MINIO_PORT:-9000}" \
    MINIO_ROOT_USER="${MINIO_ROOT_USER}" \
    MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD}" \
    MINIO_BUCKET="${MINIO_BUCKET}" \
    MINIO_URL="${MINIO_URL:-http://$MINIO_HOST:$MINIO_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Kafka
echo -e "${BLUE}  📦 Kafka${NC}"
vault kv put secret/kafka \
    KAFKA_BOOTSTRAP_SERVERS="${KAFKA_BOOTSTRAP_SERVERS}" \
    KAFKA_ADVERTISED_LISTENERS="${KAFKA_ADVERTISED_LISTENERS}" \
    KAFKA_ZOOKEEPER_CONNECT="${KAFKA_ZOOKEEPER_CONNECT:-zookeeper:2181}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Nexus
echo -e "${BLUE}  📦 Nexus${NC}"
vault kv put secret/nexus \
    NEXUS_HOST="${NEXUS_HOST:-nexus}" \
    NEXUS_PORT="${NEXUS_PORT:-8081}" \
    NEXUS_REGISTRY_PORT="${NEXUS_REGISTRY_PORT:-5000}" \
    NEXUS_USER_NAME="${NEXUS_USER_NAME}" \
    NEXUS_USER_PASSWORD="${NEXUS_USER_PASSWORD}" \
    NEXUS_ADMIN_NEW_PASS="${NEXUS_ADMIN_NEW_PASS}" \
    NEXUS_URL="${NEXUS_URL:-http://$NEXUS_HOST:$NEXUS_PORT}" \
    NEXUS_REGISTRY_URL="${NEXUS_REGISTRY_URL:-$NEXUS_HOST:$NEXUS_REGISTRY_PORT}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# GitLab
echo -e "${BLUE}  📦 GitLab${NC}"
vault kv put secret/gitlab \
    GITLAB_HOST="${GITLAB_HOST:-gitlab}" \
    GITLAB_PORT="${GITLAB_PORT:-8060}" \
    GITLAB_URL="${GITLAB_URL:-http://$GITLAB_HOST:$GITLAB_PORT}" \
    GITLAB_ROOT_PASSWORD="${GITLAB_ROOT_PASSWORD}" \
    GITLAB_ROOT_TOKEN="${GITLAB_ROOT_TOKEN}" \
    GITLAB_ACCESS_TOKEN="${GITLAB_ACCESS_TOKEN}" \
    GITLAB_USER="${GITLAB_USER}" \
    GITLAB_PASSWORD="${GITLAB_PASSWORD}" \
    GITLAB_EMAIL="${GITLAB_EMAIL:-}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# SonarQube
echo -e "${BLUE}  📦 SonarQube${NC}"
vault kv put secret/sonarqube \
    SONAR_HOST="${SONAR_HOST:-sonarqube}" \
    SONAR_PORT="${SONAR_PORT:-9000}" \
    SONAR_URL="${SONAR_URL:-http://$SONAR_HOST:$SONAR_PORT}" \
    SONAR_ADMIN="${SONAR_ADMIN:-admin}" \
    SONAR_ADMIN_PASSWORD="${SONAR_ADMIN_NEW_PASS:-admin}" \
    SONAR_ADMIN_TOKEN="${SONAR_ADMIN_TOKEN}" \
    SONAR_USER_TOKEN="${SONAR_USER_TOKEN}" \
    SONAR_JDBC_URL="${SONAR_JDBC_URL}" \
    SONAR_JDBC_USERNAME="${SONAR_JDBC_USERNAME}" \
    SONAR_JDBC_PASSWORD="${SONAR_JDBC_PASSWORD}" \
    SONAR_JENKINS_WEBHOOK_URL="${SONAR_JENKINS_WEBHOOK_URL}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Jenkins
echo -e "${BLUE}  📦 Jenkins${NC}"
vault kv put secret/jenkins \
    JENKINS_HOST="${JENKINS_HOST:-jenkins}" \
    JENKINS_PORT="${JENKINS_PORT:-8080}" \
    JENKINS_URL="${JENKINS_URL:-http://$JENKINS_HOST:$JENKINS_PORT}" \
    JENKINS_SECRET="${JENKINS_SECRET}" \
    JENKINS_AGENT_NAME="${JENKINS_AGENT_NAME}" \
    JENKINS_AGENT_WORKDIR="${JENKINS_AGENT_WORKDIR}" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# ArgoCD
echo -e "${BLUE}  📦 ArgoCD${NC}"
vault kv put secret/argocd \
    ARGO_PASSWORD="${ARGO_PASSWORD}" \
    ARGO_ADMIN_USERNAME="admin" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# JWT (генерируем случайный ключ если не задан)
echo -e "${BLUE}  📦 JWT${NC}"
JWT_SECRET="${JWT_SECRET:-$(openssl rand -hex 32)}"
vault kv put secret/jwt \
    JWT_SECRET="$JWT_SECRET" \
    JWT_ALGORITHM="HS256" \
    JWT_EXPIRATION="3600" 2>/dev/null && \
    echo -e "${GREEN}     ✅ Создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

echo ""

# =============================================================================
# Создание Vault Policies
# =============================================================================

echo -e "${GREEN}📜 Создание Vault policies...${NC}"
echo ""

# Policy для External Secrets Operator
echo -e "${BLUE}  📦 External Secrets Policy${NC}"
vault policy write external-secrets-policy - <<EOT >/dev/null 2>&1
# Чтение всех секретов в dev окружении
path "secret/data/*" {
  capabilities = ["read", "list"]
}

# Чтение метаданных (для проверки версий)
path "secret/metadata/*" {
  capabilities = ["read", "list"]
}
EOT
echo -e "${GREEN}     ✅ external-secrets-policy создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Общая политика для всех Backend'ов (admin, order, courier)
echo -e "${BLUE}  📦 Backend Policy (общая для всех backend'ов)${NC}"
vault policy write backend-policy - <<EOT >/dev/null 2>&1
# PostgreSQL
path "secret/data/postgres" {
  capabilities = ["read"]
}

# Kafka
path "secret/data/kafka" {
  capabilities = ["read"]
}

# MinIO
path "secret/data/minio" {
  capabilities = ["read"]
}

# JWT
path "secret/data/jwt" {
  capabilities = ["read"]
}
EOT
echo -e "${GREEN}     ✅ backend-policy создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

# Policy для Jenkins
echo -e "${BLUE}  📦 Jenkins Policy${NC}"
vault policy write jenkins-policy - <<EOT >/dev/null 2>&1
# Nexus
path "secret/data/nexus" {
  capabilities = ["read"]
}

# GitLab
path "secret/data/gitlab" {
  capabilities = ["read"]
}

# ArgoCD
path "secret/data/argocd" {
  capabilities = ["read"]
}

# SonarQube
path "secret/data/sonarqube" {
  capabilities = ["read"]
}
EOT
echo -e "${GREEN}     ✅ jenkins-policy создан${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка${NC}"

echo ""

# =============================================================================
# Настройка Kubernetes Authentication
# =============================================================================

echo -e "${GREEN}🔐 Настройка Kubernetes Authentication...${NC}"
echo ""

# Получение K8s API server URL
echo -e "${GREEN}📊 Получение K8s API server URL...${NC}"
K8S_HOST=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
echo -e "${BLUE}   K8s API: ${YELLOW}$K8S_HOST${NC}"
echo ""

# Получение CA сертификата K8s
echo -e "${GREEN}📊 Получение K8s CA сертификата...${NC}"
K8S_CA_CERT=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' 2>/dev/null)

# Включение Kubernetes auth method
echo -e "${GREEN}🔐 Включение Kubernetes auth method...${NC}"
if vault auth list | grep -q kubernetes; then
    echo -e "${YELLOW}   ⚠️  Kubernetes auth уже включён${NC}"
else
    vault auth enable kubernetes
    echo -e "${GREEN}   ✅ Kubernetes auth включён${NC}"
fi
echo ""

# Настройка Kubernetes auth backend
echo -e "${GREEN}⚙️  Настройка Kubernetes auth backend...${NC}"
vault write auth/kubernetes/config \
    kubernetes_host="$K8S_HOST" \
    kubernetes_ca_cert="$(echo "$K8S_CA_CERT" | base64 -d)" \
    issuer="kubernetes/serviceaccount" \
    >/dev/null 2>&1

echo -e "${GREEN}   ✅ Backend настроен${NC}"
echo ""

# =============================================================================
# Создание Vault Roles для Kubernetes Authentication
# =============================================================================

echo -e "${GREEN}🔑 Создание Vault roles для Kubernetes...${NC}"
echo ""

# ==================== Backend Roles ====================

# Общая роль для всех Backend'ов (admin, order, courier)
# Используем wildcard pattern для всех сервисов в namespace
echo -e "${BLUE}  📦 Backend Role (wildcard для *-backend)${NC}"
vault write auth/kubernetes/role/backend-role \
    bound_service_account_names="*-backend" \
    bound_service_account_namespaces=healthy-menu-dev \
    policies=backend-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

# ==================== External Secrets & Jenkins ====================

# Role для External Secrets Operator
echo -e "${BLUE}  📦 External Secrets Role${NC}"
vault write auth/kubernetes/role/external-secrets-role \
    bound_service_account_names=external-secrets-sa \
    bound_service_account_namespaces=external-secrets \
    policies=external-secrets-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

# Role для Jenkins
echo -e "${BLUE}  📦 Jenkins Role${NC}"
vault write auth/kubernetes/role/jenkins-role \
    bound_service_account_names=jenkins \
    bound_service_account_namespaces=default \
    policies=jenkins-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗"
echo -e "║  ✅  Полная инициализация Vault завершена!     ║"
echo -e "╚════════════════════════════════════════════════╝${NC}"
