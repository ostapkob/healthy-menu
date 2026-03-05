#!/bin/bash
#
# Скрипт генерации самоподписанных сертификатов для Nexus
#

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

CERT_DIR="${1:-./certs}"
NEXUS_HOST="${2:-localhost}"
NEXUS_REGISTRY_PORT="${3:-5000}"

echo -e "${BLUE}╔════════════════════════════════════════════════╗"
echo -e "║     Генерация сертификатов для Nexus           ║"
echo -e "╚════════════════════════════════════════════════╝${NC}"
echo ""

# Создаём директорию для сертификатов
mkdir -p "$CERT_DIR"

echo -e "${GREEN}📁 Директория для сертификатов: ${CERT_DIR}${NC}"

# Генерируем приватный ключ
echo -e "${GREEN}🔑 Генерация приватного ключа...${NC}"
openssl genrsa -out "${CERT_DIR}/nexus-key.pem" 4096

# Генерируем CSR (Certificate Signing Request)
echo -e "${GREEN}📝 Генерация CSR...${NC}"
openssl req -new -key "${CERT_DIR}/nexus-key.pem" \
    -out "${CERT_DIR}/nexus.csr" \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=HealthyMenu/OU=DevOps/CN=${NEXUS_HOST}" \
    -addext "subjectAltName=DNS:${NEXUS_HOST},DNS:nexus,DNS:localhost,IP:127.0.0.1,IP:192.168.49.2"

# Генерируем самоподписанный сертификат
echo -e "${GREEN}📜 Генерация самоподписанного сертификата...${NC}"
openssl x509 -req -days 3650 \
    -in "${CERT_DIR}/nexus.csr" \
    -signkey "${CERT_DIR}/nexus-key.pem" \
    -out "${CERT_DIR}/nexus.crt" \
    -extfile <(echo "subjectAltName=DNS:${NEXUS_HOST},DNS:nexus,DNS:localhost,IP:127.0.0.1,IP:192.168.49.2")

# Устанавливаем правильные права
chmod 600 "${CERT_DIR}/nexus-key.pem"
chmod 644 "${CERT_DIR}/nexus.crt"

echo ""
echo -e "${GREEN}✅ Сертификаты сгенерированы!${NC}"
echo ""
echo "📂 Файлы:"
echo "   - ${CERT_DIR}/nexus-key.pem (приватный ключ)"
echo "   - ${CERT_DIR}/nexus.crt (публичный сертификат)"
echo "   - ${CERT_DIR}/nexus.csr (запрос на подпись)"
echo ""

# Копируем сертификат в системные хранилища (требуется sudo)
echo -e "${YELLOW}📋 Копирование сертификата в системные хранилища...${NC}"

# Для Linux
if command -v update-ca-certificates &> /dev/null; then
    echo "   🐧 Debian/Ubuntu detected"
    sudo cp "${CERT_DIR}/nexus.crt" /usr/local/share/ca-certificates/nexus.crt
    sudo update-ca-certificates
    echo "   ✅ Сертификат добавлен в системное хранилище"
elif command -v trust &> /dev/null; then
    echo "   🎩 RHEL/CentOS/Fedora detected"
    sudo cp "${CERT_DIR}/nexus.crt" /etc/pki/ca-trust/source/anchors/nexus.crt
    sudo update-ca-trust
    echo "   ✅ Сертификат добавлен в системное хранилище"
else
    echo "   ⚠️  Не удалось определить систему. Добавьте сертификат вручную."
fi

# Для Docker daemon
echo ""
echo -e "${YELLOW}🐳 Настройка Docker daemon...${NC}"
echo "   Создаём директорию для сертификатов Docker..."

# Создаём директорию для сертификатов Docker
DOCKER_CERT_DIR="/etc/docker/certs.d/${NEXUS_HOST}:${NEXUS_REGISTRY_PORT}"
sudo mkdir -p "$DOCKER_CERT_DIR"
sudo cp "${CERT_DIR}/nexus.crt" "${DOCKER_CERT_DIR}/ca.crt"

# Также для localhost
DOCKER_CERT_DIR_LOCAL="/etc/docker/certs.d/localhost:${NEXUS_REGISTRY_PORT}"
sudo mkdir -p "$DOCKER_CERT_DIR_LOCAL"
sudo cp "${CERT_DIR}/nexus.crt" "${DOCKER_CERT_DIR_LOCAL}/ca.crt"

# Для minikube если используется
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    echo "   🎯 Minikube detected, copying certificate..."
    minikube ssh "sudo mkdir -p /etc/docker/certs.d/${NEXUS_HOST}:${NEXUS_REGISTRY_PORT}"
    minikube ssh "sudo cp /tmp/nexus.crt /etc/docker/certs.d/${NEXUS_HOST}:${NEXUS_REGISTRY_PORT}/ca.crt" 2>/dev/null || true
fi

echo "   ✅ Docker daemon настроен"

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗"
echo -e "║  ✅ Генерация и настройка сертификатов         ║"
echo -e "║     завершена!                                   ║"
echo -e "╚════════════════════════════════════════════════╝${NC}"
echo ""
echo "📝 Следующие шаги:"
echo "   1. Перезапустите Docker daemon: sudo systemctl restart docker"
echo "   2. Обновите конфигурацию Nexus в Terraform"
echo "   3. Пересоздайте контейнер Nexus"
echo ""
