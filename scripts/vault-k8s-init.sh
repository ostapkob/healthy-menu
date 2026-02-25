#!/bin/bash
#
# Скрипт настройки Kubernetes Authentication в Vault
# Создаёт K8s auth method и роли для ServiceAccount
#

set -e

# Цвета
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Загрузка переменных из .env если есть
ENV_FILE="${1:-./.env}"
if [ -f "$ENV_FILE" ]; then
    echo -e "${BLUE}📄 Загрузка переменных из $ENV_FILE${NC}"
    set -a
    source "$ENV_FILE"
    set +a
fi

# Переменные (окружение > .env > default)
VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
VAULT_TOKEN="${VAULT_TOKEN:-vault-root-token}"
K8S_CONTEXT="${K8S_CONTEXT:-}"

# Экспорт переменных окружения
export VAULT_ADDR
export VAULT_TOKEN

echo -e "${BLUE}╔════════════════════════════════════════════════╗"
echo -e "║  Vault Kubernetes Auth Configuration Script    ║"
echo -e "╚════════════════════════════════════════════════╝${NC}"
echo ""

# Проверка доступности Vault
echo -e "${GREEN}📊 Проверка доступности Vault...${NC}"
if ! vault status >/dev/null 2>&1; then
    echo -e "${RED}❌ Vault не доступен по адресу $VAULT_ADDR${NC}"
    echo -e "${YELLOW}💡 Убедись, что Vault запущен:${NC}"
    echo -e "   ${BLUE}docker ps | grep vault${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Vault доступен${NC}"
echo ""

# Проверка kubectl
echo -e "${GREEN}📊 Проверка kubectl...${NC}"
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl не найден${NC}"
    echo -e "${YELLOW}💡 Установи kubectl: https://kubernetes.io/docs/tasks/tools/${NC}"
    exit 1
fi
echo -e "${GREEN}✅ kubectl доступен${NC}"
echo ""

# Получение K8s контекста
if [ -z "$K8S_CONTEXT" ]; then
    K8S_CONTEXT=$(kubectl config current-context 2>/dev/null || echo "")
    if [ -z "$K8S_CONTEXT" ]; then
        echo -e "${RED}❌ Не удалось определить текущий kubectl контекст${NC}"
        echo -e "${YELLOW}💡 Установи контекст или передай через K8S_CONTEXT=${NC}"
        exit 1
    fi
fi
echo -e "${BLUE}📍 K8s контекст: ${YELLOW}$K8S_CONTEXT${NC}"
echo ""

# Получение K8s API server URL
echo -e "${GREEN}📊 Получение K8s API server URL...${NC}"
K8S_HOST=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
echo -e "${BLUE}   K8s API: ${YELLOW}$K8S_HOST${NC}"
echo ""

# Получение CA сертификата K8s
echo -e "${GREEN}📊 Получение K8s CA сертификата...${NC}"
K8S_CA_CERT=$(kubectl config view --raw --minify --flatten -o jsonpath='{.clusters[0].cluster.certificate-authority-data}' 2>/dev/null)

# Если CA не найден в конфиге, пробуем скачать
if [ -z "$K8S_CA_CERT" ]; then
    echo -e "${YELLOW}   CA не найден в kubeconfig, скачиваем...${NC}"
    K8S_CA_CERT=$(curl -sk "$K8S_HOST/.well-known/openid-configuration" | jq -r '.jwks_uri' 2>/dev/null | sed 's|/openid/v1/jwks||' | xargs -I {} curl -sk {} | jq -r '.keys[0].x5c[0]' 2>/dev/null)

    # Если всё ещё пусто, используем стандартный путь для Minikube
    if [ -z "$K8S_CA_CERT" ]; then
        if [ -f ~/.minikube/ca.crt ]; then
            K8S_CA_CERT=$(base64 -w0 ~/.minikube/ca.crt)
        elif [ -f ~/.kube/ca.crt ]; then
            K8S_CA_CERT=$(base64 -w0 ~/.kube/ca.crt)
        else
            echo -e "${RED}❌ Не удалось получить CA сертификат${NC}"
            echo -e "${YELLOW}💡 Для Minikube: ~/.minikube/ca.crt${NC}"
            echo -e "${YELLOW}💡 Для k3d/kind: ~/.kube/ca.crt${NC}"
            exit 1
        fi
    fi
fi
echo -e "${GREEN}✅ CA сертификат получен${NC}"
echo ""

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
# Создание ролей Vault для каждого ServiceAccount
# =============================================================================

echo -e "${GREEN}🔑 Создание Vault roles для ServiceAccount...${NC}"
echo ""

# -----------------------------------------------------------------------------
# Role для External Secrets Operator
# -----------------------------------------------------------------------------
echo -e "${BLUE}  📦 External Secrets Operator${NC}"
vault write auth/kubernetes/role/external-secrets-role \
    bound_service_account_names=external-secrets-sa \
    bound_service_account_namespaces=external-secrets \
    policies=external-secrets-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

# -----------------------------------------------------------------------------
# Role для Admin Backend
# -----------------------------------------------------------------------------
echo -e "${BLUE}  📦 Admin Backend${NC}"
vault write auth/kubernetes/role/admin-backend-role \
    bound_service_account_names=admin-backend \
    bound_service_account_namespaces=healthy-menu-dev \
    policies=admin-backend-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

# -----------------------------------------------------------------------------
# Role для Order Backend
# -----------------------------------------------------------------------------
echo -e "${BLUE}  📦 Order Backend${NC}"
vault write auth/kubernetes/role/order-backend-role \
    bound_service_account_names=order-backend \
    bound_service_account_namespaces=healthy-menu-dev \
    policies=order-backend-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

# -----------------------------------------------------------------------------
# Role для Courier Backend
# -----------------------------------------------------------------------------
echo -e "${BLUE}  📦 Courier Backend${NC}"
vault write auth/kubernetes/role/courier-backend-role \
    bound_service_account_names=courier-backend \
    bound_service_account_namespaces=healthy-menu-dev \
    policies=courier-backend-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

# -----------------------------------------------------------------------------
# Role для Jenkins
# -----------------------------------------------------------------------------
echo -e "${BLUE}  📦 Jenkins${NC}"
vault write auth/kubernetes/role/jenkins-role \
    bound_service_account_names=jenkins \
    bound_service_account_namespaces=default \
    policies=jenkins-policy \
    ttl=1h \
    >/dev/null 2>&1 && \
    echo -e "${GREEN}     ✅ Role создана${NC}" || echo -e "${YELLOW}     ⚠️  Ошибка (возможно уже существует)${NC}"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗"
echo -e "║  ✅  Kubernetes auth настроен!                 ║"
echo -e "╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📝 Следующие шаги:${NC}"
echo ""
echo -e "  ${YELLOW}1.${NC} Активируй роли в terraform/vault-policies.tf"
echo -e "     (раскомментируй ресурсы vault_kubernetes_auth_backend_role)"
echo ""
echo -e "  ${YELLOW}2.${NC} Примени Terraform:"
echo -e "     ${BLUE}cd terraform && terraform apply -auto-approve${NC}"
echo ""
echo -e "  ${YELLOW}3.${NC} Проверь роли в Vault:"
echo -e "     ${BLUE}vault read auth/kubernetes/role/external-secrets-role${NC}"
echo ""
echo -e "  ${YELLOW}4.${NC} Установи External Secrets Operator (следующий шаг)"
echo ""
