# !/bin/bash

# Включаем строгий режим
# set -euo pipefail

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

echo "-----------------GITLAB-----------------"

# Проверяем обязательные переменные
: "${GITLAB_URL:?Не задана GITLAB_URL}"
: "${GITLAB_CONTAINER_NAME:?Не задана GITLAB_CONTAINER_NAME}"
: "${GITLAB_USER:?Не задана GITLAB_USER}"
: "${GITLAB_NAME:?Не задана GITLAB_NAME}"
: "${GITLAB_EMAIL:?Не задана GITLAB_EMAIL}"
: "${GITLAB_PASSWORD:?Не задана GITLAB_PASSWORD}"
: "${GITLAB_ROOT_PASSWORD:?Не задана GITLAB_ROOT_PASSWORD}"

echo -e "${green}🔧 GitLab Configuration Script${reset}"
echo -e "${green}============================${reset}"
echo -e "${green}URL: ${pink}${GITLAB_URL}${reset}"
echo -e "${green}Container: ${pink}${GITLAB_CONTAINER_NAME}${reset}"
echo -e "${green}User: ${pink}${GITLAB_USER}${reset}"
echo -e "${green}Name: ${pink}${GITLAB_NAME}${reset}"
echo -e "${green}Email: ${pink}${GITLAB_EMAIL}${reset}"

if ! curl -sSf --max-time 5 --head "$GITLAB_URL" >/dev/null; then
  echo "Host $GITLAB_URL недоступен (timeout)" >&2
  exit 1
fi

# Вычисляем дату истечения токена (+2 месяца от текущей даты)
EXPIRES_AT=$(date -d "+2 months" +%Y-%m-%d)
echo -e "${green}📅 Token expiry: ${pink}${EXPIRES_AT}${reset}"

# Шаг 0: Ожидаем запуск GitLab и появление initial password
echo -e "${green}⏳ Waiting for GitLab to start...${reset}"
MAX_WAIT=1200  # 20 минут
COUNTER=0

while true; do
    # Проверяем, запущен ли контейнер
    if docker ps | grep -q "${GITLAB_CONTAINER_NAME}"; then
        # Проверяем, появился ли initial password
        if docker exec "${GITLAB_CONTAINER_NAME}" test -f /etc/gitlab/initial_root_password 2>/dev/null; then
            break
        fi
    fi

    sleep 10
    COUNTER=$((COUNTER + 10))
    echo -e "${green}   Waiting... ${COUNTER}s${reset}"

    if [ $COUNTER -ge $MAX_WAIT ]; then
        echo -e "${red}❌ GitLab didn't start in ${MAX_WAIT} seconds${reset}"
        echo -e "${red}   Check logs: docker logs ${GITLAB_CONTAINER_NAME}${reset}"
        exit 1
    fi
done

# Шаг 1: Получаем initial root password
echo -e "${green}🔑 Getting initial root password...${reset}"
INITIAL_ROOT_PASSWORD=$(docker exec "${GITLAB_CONTAINER_NAME}" cat /etc/gitlab/initial_root_password 2>/dev/null | grep -o '^[^[:space:]]*' || echo "")

if [ -z "${INITIAL_ROOT_PASSWORD}" ]; then
    echo -e "${red}❌ Error: Could not get initial root password!${reset}"
    echo -e "${red}   Check: docker exec ${GITLAB_CONTAINER_NAME} cat /etc/gitlab/initial_root_password${reset}"
    exit 1
fi
echo -e "${green}✅ Initial root password obtained${reset}"

# Шаг 2: Меняем пароль root на GITLAB_ROOT_PASSWORD
echo -e "${green}🔄 Changing root password to provided password...${reset}"
if ! CHANGE_PASSWORD_OUTPUT=$(docker exec -i "${GITLAB_CONTAINER_NAME}" gitlab-rails runner "
  user = User.find_by_username('root');
  user.password = '${GITLAB_ROOT_PASSWORD}';
  user.password_confirmation = '${GITLAB_ROOT_PASSWORD}';
  user.save!
" 2>&1); then
    echo -e "${red}❌ Error changing root password: ${CHANGE_PASSWORD_OUTPUT}${reset}"
    exit 1
else
    echo -e "${green}✅ Root password changed successfully!${reset}"
fi

# Ждём немного после смены пароля
sleep 5

# Шаг 3: Создаём Personal Access Token для root
echo -e "${green}🔑 Creating Personal Access Token for root...${reset}"
ROOT_TOKEN=$(docker exec -i "${GITLAB_CONTAINER_NAME}" gitlab-rails runner "
  user = User.find_by_username('root');
  token = user.personal_access_tokens.create(scopes: [:api, :read_user, :read_api, :read_repository, :write_repository], name: 'Automation Token', expires_at: Date.parse('${EXPIRES_AT}'));
  puts token.token
" 2>&1 | tail -1)

if [ -z "${ROOT_TOKEN}" ] || [[ "${ROOT_TOKEN}" == *"error"* ]]; then
    echo -e "${red}❌ Error creating root token!${reset}"
    echo -e "${red}   Output: ${ROOT_TOKEN}${reset}"
    exit 1
fi
echo -e "${green}✅ Root token created${reset}"

# Шаг 4: Создаём пользователя ${GITLAB_USER}
echo -e "${green}👤 Creating user ${GITLAB_USER}...${reset}"
CREATE_USER_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" \
    -H "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=${GITLAB_USER}&name=${GITLAB_NAME}&email=${GITLAB_EMAIL}&password=${GITLAB_PASSWORD}&skip_confirmation=true" \
    "${GITLAB_URL}/api/v4/users")

HTTP_STATUS=$(echo "${CREATE_USER_RESPONSE}" | sed -n 's/.*HTTPSTATUS:\([0-9][0-9]*\).*/\1/p')
BODY=$(echo "${CREATE_USER_RESPONSE}" | sed 's/HTTPSTATUS:[0-9]*//g')

echo "Debug: HTTP ${HTTP_STATUS}, Body first 100: ${BODY:0:100}"

if [ "${HTTP_STATUS}" = "201" ]; then
    USER_ID=$(echo "${BODY}" | jq -r '.id')
    echo -e "${green}✅ User ${GITLAB_USER} created with ID: ${pink}${USER_ID}${reset}"
else
    echo -e "${red}❌ Error creating user! HTTP ${HTTP_STATUS}${reset}"
    echo "${BODY}" | jq '. // empty'
    exit 1
fi

# Шаг 5: Создаём token для ${GITLAB_USER}
echo -e "${green}🔑 Creating token for ${GITLAB_USER}...${reset}"
CREATE_TOKEN_RESPONSE=$(curl -s --header "PRIVATE-TOKEN: ${ROOT_TOKEN}" \
    --data "name=${GITLAB_NAME}" \
    --data "scopes[]=api" \
    --data "expires_at=${EXPIRES_AT}" \
    --request POST "${GITLAB_URL}/api/v4/users/${USER_ID}/personal_access_tokens")
USER_TOKEN=$(echo "${CREATE_TOKEN_RESPONSE}" | jq -r '.token')

if [ -z "${USER_TOKEN}" ] || [ "${USER_TOKEN}" = "null" ]; then
    echo -e "${red}❌ Error creating user token! Response: ${CREATE_TOKEN_RESPONSE}${reset}"
    exit 1
fi
echo -e "${green}✅ Token for ${GITLAB_USER} created${reset}"

# Шаг 6: Добавляем jenkins в whitelist
echo -e "${green}🌐 Add jenkins в whitelist...${reset}"
docker exec -it "${GITLAB_CONTAINER_NAME}" gitlab-rails runner "
  settings = ApplicationSetting.current;
  settings.update!(
    allow_local_requests_from_web_hooks_and_services: true,
    outbound_local_requests_whitelist: ['jenkins:8080']
  )"


# Финал
echo -e "${green}🎉 GitLab configuration complete!${reset}"
echo -e "${green}🌐 URL: ${pink}${GITLAB_URL}${reset}"
echo -e "${green}👤 Root: root / ${GITLAB_ROOT_PASSWORD}${reset}"
echo -e "${green}👤 User: ${GITLAB_USER} / ${GITLAB_PASSWORD}${reset}"
echo -e "${green}🔑 GITLAB_ROOT_TOKEN=${pink}${ROOT_TOKEN}${reset}"
echo -e "${green}🔑 GITLAB_ACCESS_TOKEN=${pink}${USER_TOKEN}${reset}"
echo -e "${green}📋 Save these tokens for future use:${reset}"

