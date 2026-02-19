#!/usr/bin/env bash
set -euo pipefail


pink='\033[1;35m'
green='\033[0;32m'
red='\033[0;31m'
reset='\033[0m'
ENV="./.env"

echo -e "${pink}-----------------SONARQUBE-----------------${reset}"

if [ -f "${ENV}" ]; then
    set -o allexport
    source "${ENV}"
    set +o allexport
else
    echo -e "${red}❌ Ошибка: файл ${ENV} не найден!${reset}"
    exit 1
fi

# Проверяем обязательные переменные
: "${SONAR_ADMIN:?Не задана SONAR_ADMIN}"
: "${SONAR_ADMIN_PASS:?Не задана SONAR_ADMIN_PASS}"
: "${SONAR_ADMIN_NEW_PASS:?Не задана SONAR_ADMIN_NEW_PASS}"
: "${SONAR_USER_LOGIN:?Не задан SONAR_USER_LOGIN}"
: "${SONAR_USER_NAME:?Не задан SONAR_USER_NAME}"
: "${SONAR_USER_EMAIL:?Не задан SONAR_USER_EMAIL}"
: "${SONAR_USER_PASS:?Не задан SONAR_USER_PASS}"
: "${SONAR_TOKEN_NAME:?Не задано SONAR_TOKEN_NAME}"
: "${SONAR_JENKINS_WEBHOOK_URL:?Не задан SONAR_JENKINS_WEBHOOK_URL}"
: "${SONAR_HOST:?Не задан SONAR_HOST}"
: "${SONAR_PORT:?Не задан SONAR_PORT}"
SONAR_URL="http://${SONAR_HOST}:${SONAR_PORT}"


# Генерируем дату истечения +2 месяца
EXPIRATION=$(date -d "+2 months" +%Y-%m-%d)
echo "Дата истечения токенов: ${EXPIRATION}"

# 1. Меняем пароль admin
echo "🔄 Меняем ${SONAR_ADMIN}:${SONAR_ADMIN_PASS}"
curl -u admin:admin -X POST "{$SONAR_URL}/api/users/change_password?login=admin&previousPassword=admin&password=${SONAR_ADMIN_NEW_PASS}"
sleep 1

curl -sS -u "${SONAR_ADMIN}:${SONAR_ADMIN_NEW_PASS}" \
  "${SONAR_URL}/api/authentication/validate" | jq .

echo "✅ Пароль admin изменён на ${SONAR_ADMIN_NEW_PASS}"

# 2. Создаём нового пользователя
echo "🔄 Создаём пользователя ${SONAR_USER_LOGIN}..."
curl -sS -u "${SONAR_ADMIN}:${SONAR_ADMIN_NEW_PASS}" -X POST \
  "${SONAR_URL}/api/users/create" \
  -d "login=${SONAR_USER_LOGIN}" \
  -d "name=${SONAR_USER_NAME}" \
  -d "email=${SONAR_USER_EMAIL}" \
  -d "password=${SONAR_USER_PASS}" \
  -d "password_confirmation=${SONAR_USER_PASS}" >/dev/null

echo "✅ Пользователь ${SONAR_USER_LOGIN} создан"

# 3. Меняем пароль нового пользователя (опционально)
echo "🔄 Меняем пароль пользователя ${SONAR_USER_LOGIN}..."
curl -sS -u "${SONAR_USER_LOGIN}:${SONAR_USER_PASS}" -X POST \
  "${SONAR_URL}/api/users/change_password" \
  -d "login=${SONAR_USER_LOGIN}&previousPassword=${SONAR_USER_PASS}&password=${SONAR_USER_PASS}&password_confirmation=${SONAR_USER_PASS}" >/dev/null

echo "✅ Пароль ${SONAR_USER_LOGIN} подтверждён"

# 4. Создаём глобальный webhook для Jenkins (если не существует)
echo "🔄 Создаём webhook для Jenkins..."
# Проверяем, существует ли уже webhook с таким URL
existing_webhooks="$(curl -sS -u "${SONAR_ADMIN}:${SONAR_ADMIN_NEW_PASS}" "${SONAR_URL}/api/webhooks/list")"
if echo "${existing_webhooks}" | jq -e ".webhooks[] | select(.url == \"${SONAR_JENKINS_WEBHOOK_URL}\")" >/dev/null 2>&1; then
  echo "✅ Webhook ${SONAR_JENKINS_WEBHOOK_URL} уже существует"
else
  curl -sS -u "${SONAR_ADMIN}:${SONAR_ADMIN_NEW_PASS}" -X POST \
    "${SONAR_URL}/api/webhooks/create" \
    -d "name=jenkins-webhook" \
    -d "url=${SONAR_JENKINS_WEBHOOK_URL}" >/dev/null
  echo "✅ Глобальный webhook для Jenkins создан"
fi

# 5. Создаём токен для admin
echo "🔄 Создаём токен для admin..."
DATA="name=${SONAR_TOKEN_NAME}-admin&type=GLOBAL_ANALYSIS_TOKEN&expirationDate=${EXPIRATION}"
resp_admin="$(curl -sS -u "${SONAR_ADMIN}:${SONAR_ADMIN_NEW_PASS}" \
  -X POST "${SONAR_URL}/api/user_tokens/generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "${DATA}")"

ADMIN_TOKEN="$(printf '%s\n' "${resp_admin}" | jq -r '.token')"
if [[ "${ADMIN_TOKEN}" == "null" || -z "${ADMIN_TOKEN}" ]]; then
  echo "❌ Ошибка токена admin: ${resp_admin}"
  exit 1
fi

# 6. Создаём токен для нового пользователя
echo "🔄 Создаём токен для ${SONAR_USER_LOGIN}..."
DATA="name=${SONAR_TOKEN_NAME}-user&type=GLOBAL_ANALYSIS_TOKEN&expirationDate=${EXPIRATION}"
resp_user="$(curl -sS -u "${SONAR_USER_LOGIN}:${SONAR_USER_PASS}" \
  -X POST "${SONAR_URL}/api/user_tokens/generate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "${DATA}")"

USER_TOKEN="$(printf '%s\n' "${resp_user}" | jq -r '.token')"
if [[ "${USER_TOKEN}" == "null" || -z "${USER_TOKEN}" ]]; then
  echo "❌ Ошибка токена user: ${resp_user}"
  exit 1
fi


# Замена
sed -i -E "s/^SONAR_ADMIN_TOKEN=.*/SONAR_ADMIN_TOKEN=${ADMIN_TOKEN//\//\\/}/" "$ENV"
sed -i -E "s/^SONAR_ADMIN_TOKEN=.*/SONAR_ADMIN_TOKEN=${USER_TOKEN//\//\\/}/" "$ENV"

 
# Вывод результатов
echo -e "\n🎉 Результаты:"
echo -e "${green}🔑 SONAR_ADMIN_TOKEN=${pink}${ADMIN_TOKEN}${reset}"
echo -e "${green}🔑 SONAR_USER_TOKEN=${pink}${USER_TOKEN}${reset}"
