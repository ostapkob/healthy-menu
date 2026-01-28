# !/bin/bash

# Включаем строгий режим
set -euo pipefail

# Цвета для вывода
pink='\033[1;35m'
green='\033[0;32m'
red='\033[0;31m'
reset='\033[0m'

# Имя файла .env
ENV="./.env"

# Загружаем .env
if [ -f "${ENV}" ]; then
    set -o allexport
    source "${ENV}"
    set +o allexport
else
    echo -e "${red}❌ Ошибка: файл ${ENV} не найден!${reset}"
    exit 1
fi

# Проверяем обязательные переменные
: "${GITLAB_URL?Не задана GITLAB_URL в .env}"
: "${GITLAB_CONTAINER_NAME?Не задана GITLAB_CONTAINER_NAME в .env}"
: "${GITLAB_USER?Не задана GITLAB_USER в .env}"
: "${GITLAB_NAME?Не задана GITLAB_NAME в .env}"
: "${GITLAB_EMAIL?Не задана GITLAB_EMAIL в .env}"
: "${GITLAB_PASSWORD?Не задана GITLAB_PASSWORD в .env}"
: "${GITLAB_ROOT_PASSWORD?Не задана GITLAB_ROOT_PASSWORD в .env (для смены пароля root)}"

# Вычисляем дату истечения токена (+2 месяца от текущей даты)
EXPIRES_AT=$(date -d "+2 months" +%Y-%m-%d)
echo -e "${green}📅 Дата истечения токенов: ${pink}${EXPIRES_AT}${reset}"

# Шаг 1: Получаем initial root password
echo -e "${green}🔑 Получаем initial root password...${reset}"
INITIAL_ROOT_PASSWORD=$(docker exec "${GITLAB_CONTAINER_NAME}" cat /etc/gitlab/initial_root_password 2>/dev/null || echo "")
if [ -z "${INITIAL_ROOT_PASSWORD}" ]; then
    echo -e "${red}❌ Ошибка: Не удалось получить initial root password!${reset}"
    exit 1
fi
echo -e "${green}✅ Initial root password: ${pink}${INITIAL_ROOT_PASSWORD}${reset} (используем для настройки).${reset}"

# Шаг 2: Меняем пароль root на GITLAB_ROOT_PASSWORD через Rails console
echo -e "${green}🔄 Меняем пароль root на ${pink}${GITLAB_ROOT_PASSWORD}${reset}...${reset}"
if ! CHANGE_PASSWORD_OUTPUT=$(docker exec -i "${GITLAB_CONTAINER_NAME}" gitlab-rails runner "
  user = User.find_by_username('root');
  user.password = '${GITLAB_ROOT_PASSWORD}';
  user.password_confirmation = '${GITLAB_ROOT_PASSWORD}';
  user.save!
" 2>&1); then
    echo -e "${red}❌ Ошибка при смене пароля root: ${CHANGE_PASSWORD_OUTPUT}${reset}"
    exit 1
else
    echo -e "${green}✅ Пароль root успешно изменён!${reset}"
fi

# Шаг 3: Создаём Personal Access Token для root
echo -e "${green}🔑 Создаём Personal Access Token для root...${reset}"
ROOT_TOKEN=$(docker exec -i "${GITLAB_CONTAINER_NAME}" gitlab-rails runner "
  user = User.find_by_username('root');
  token = user.personal_access_tokens.create(scopes: [:api, :read_user, :read_api, :read_repository, :write_repository], name: 'Automation Token', expires_at: Date.parse('${EXPIRES_AT}'));
  puts token.token
")
if [ -z "${ROOT_TOKEN}" ]; then
    echo -e "${red}❌ Ошибка: Не удалось создать root token!${reset}"
    exit 1
fi
echo -e "${green}✅ Root token создан: ${pink}${ROOT_TOKEN}${reset}"

# Шаг 4: Создаём пользователя ${GITLAB_USER}
echo -e "${green}👤 Создаём пользователя ${GITLAB_USER}...${reset}"
CREATE_USER_RESPONSE=$(curl -s --header "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
    --data "username=${GITLAB_USER}" \
    --data "name=${GITLAB_NAME}" \
    --data "email=${GITLAB_EMAIL}" \
    --data "password=${GITLAB_PASSWORD}" \
    --data "skip_confirmation=true" \
    --request POST "${GITLAB_URL}api/v4/users")
USER_ID=$(echo "${CREATE_USER_RESPONSE}" | jq -r '.id')
if [ -z "${USER_ID}" ] || [ "${USER_ID}" = "null" ]; then
    echo -e "${red}❌ Ошибка: Не удалось создать пользователя! Ответ: ${CREATE_USER_RESPONSE}${reset}"
    exit 1
fi
echo -e "${green}✅ Пользователь ${GITLAB_USER} создан с ID: ${pink}${USER_ID}${reset}"

# Шаг 5: Создаём token для ${GITLAB_USER}
echo -e "${green}🔑 Создаём token для ${GITLAB_USER}...${reset}"
CREATE_TOKEN_RESPONSE=$(curl -s --header "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
    --data "name=${GITLAB_NAME}" \
    --data "scopes[]=api" \
    --data "expires_at=${EXPIRES_AT}" \
    --request POST "${GITLAB_URL}api/v4/users/${USER_ID}/personal_access_tokens")
USER_TOKEN=$(echo "${CREATE_TOKEN_RESPONSE}" | jq -r '.token')
if [ -z "${USER_TOKEN}" ] || [ "${USER_TOKEN}" = "null" ]; then
    echo -e "${red}❌ Ошибка: Не удалось создать token! Ответ: ${CREATE_TOKEN_RESPONSE}${reset}"
    exit 1
fi
echo -e "${green}✅ Token для ${GITLAB_USER}: ${pink}${USER_TOKEN}${reset}"

# Шаг 6: Сохраняем токены в .env
function save_to_env {
    local KEY="$1"
    local VALUE="$2"
    escaped_value=$(printf '%s' "$VALUE" | sed 's/[&|]/\\&/g')
    if grep -qE "^${KEY}=" "${ENV}"; then
        sed -i "s|^${KEY}=.*|${KEY}=${escaped_value}|" "${ENV}"
    else
        printf '%s=%s\n' "$KEY" "$VALUE" >> "${ENV}"
    fi
    echo -e "${green}✅ ${KEY} сохранён в ${ENV}.${reset}"
}

save_to_env "GITLAB_ROOT_TOKEN" "${ROOT_TOKEN}"
save_to_env "GITLAB_ACCESS_TOKEN" "${USER_TOKEN}"

# Финал
echo -e "${green}🎉 Готово! GitLab доступен по ${pink}${GITLAB_URL}${reset}"
echo -e "${green}✅ Root token сохранён в .env как GITLAB_ROOT_TOKEN.${reset}"
echo -e "${green}✅ Пользователь ${GITLAB_USER} готов с токеном в .env как GITLAB_ACCESS_TOKEN.${reset}"

