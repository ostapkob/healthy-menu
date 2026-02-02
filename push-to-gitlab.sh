#!/bin/bash

ENV="./.env"
pink='\033[1;35m'
green='\033[0;32m'
red='\033[0;31m'
yellow='\033[1;33m'
blue='\033[0;34m'
reset='\033[0m'

# Загружаем .env
if [ -f "${ENV}" ]; then
    set -o allexport
    source "${ENV}"
    set +o allexport
else
    echo -e "${red}❌ Ошибка: файл ${ENV} не найден!${reset}"
    exit 1
fi

# Display GitLab URL for confirmation
echo -e "${green}URL: $GITLAB_URL${reset}"

# Use token from environment (fallback to input if needed)
ACCESS_TOKEN="$GITLAB_ACCESS_TOKEN"
# if [ -z "$ACCESS_TOKEN" ]; then
#   echo -e "${yellow}🔑 Введите личный токен доступа:${reset}"
#   read -s ACCESS_TOKEN
# fi

if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "${red}❌ Токен не введен${reset}"
  exit 1
fi

# Validate access token
echo -e "${blue}🔍 Проверяем токен...${reset}"
USER_INFO=$(curl -s "$GITLAB_URL/api/v4/user" -H "PRIVATE-TOKEN: $ACCESS_TOKEN")

if echo "$USER_INFO" | grep -q "\"username\""; then
  USERNAME=$(echo "$USER_INFO" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  echo -e "${green}✅ Токен действителен. Пользователь: $USERNAME${reset}"
else
  echo -e "${red}❌ Неверный токен${reset}"
  exit 1
fi

# List of repositories to process
REPOSITORIES=(
  "admin-backend"
  "admin-frontend"
  "courier-backend"
  "courier-frontend"
  "order-backend"
  "order-frontend"
  "ci-pipelines"
  "healthy-menu-gitops"
  "healthy-menu-infra"
)

# Prompt for commit message
echo -e "${yellow}📝 Введите сообщение для коммита:${reset}"
read -r COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
  echo -e "${red}❌ Сообщение для коммита не введено${reset}"
  exit 1
fi

echo ""
echo -e "${pink}📁 Обработка ${#REPOSITORIES[@]} репозиториев...${reset}"
echo "========================================"

# Webhook configuration
WEBHOOK_URL="http://jenkins:8080/generic-webhook-trigger/invoke?token=gitlab-mr-build"
PUSH_EVENTS=true
MERGE_REQUEST_EVENTS=true
ENABLE_SSL_VERIFICATION=false

# Function to add webhook if not exists
add_webhook() {
  local project_id="$1"
 
  # Check existing hooks
  hooks=$(curl -s "$GITLAB_URL/api/v4/projects/$project_id/hooks" -H "PRIVATE-TOKEN: $ACCESS_TOKEN")
 
  if echo "$hooks" | grep -q "\"url\":\"$WEBHOOK_URL\""; then
    echo -e "${yellow}Webhook уже существует${reset}"
    return 0
  fi
 
  response=$(curl -s -X POST "$GITLAB_URL/api/v4/projects/$project_id/hooks" \
    -H "PRIVATE-TOKEN: $ACCESS_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"$WEBHOOK_URL\", \"push_events\":$PUSH_EVENTS, \"merge_requests_events\":$MERGE_REQUEST_EVENTS, \"enable_ssl_verification\":$ENABLE_SSL_VERIFICATION}")
 
  if echo "$response" | grep -q "\"id\""; then
    echo -e "${green}Webhook добавлен${reset}"
    return 0
  else
    echo -e "${red}Ошибка добавления webhook: $response${reset}"
    return 1
  fi
}

# Function to setup and push local repo
setup_and_push() {
  local repo="$1"

  # Copy .gitignore if it exists in parent
  if [ -f "../.gitignore" ]; then
    cp "../.gitignore" .
  fi

  # Initialize git if not already
  if [ ! -d ".git" ]; then
    git init
    echo -e "${blue}🔄 Инициализирован git в $repo${reset}"
  fi

  # Add changes and commit
  git add .
  if ! git commit -m "$COMMIT_MESSAGE"; then
    echo -e "${yellow}⚠️ Нет изменений для коммита в $repo${reset}"
  fi

  # Set remote if not already set
  git remote add origin "$GITLAB_URL/$USERNAME/$repo.git" 2>/dev/null

  # Push changes
  if git push -u origin master; then
    echo -e "${green}✅ Успешно запушено в $repo${reset}"
  else
    echo -e "${red}❌ Ошибка пуша в $repo${reset}"
    return 1
  fi

  return 0
}

# Process each repository
for repo in "${REPOSITORIES[@]}"; do
  echo -en "${pink}• $repo:${reset} "

  # Check if repository exists
  existing=$(curl -s "$GITLAB_URL/api/v4/projects?search=$repo" \
    -H "PRIVATE-TOKEN: $ACCESS_TOKEN" | grep -o "\"path\":\"$repo\"")

  if [ -n "$existing" ]; then
    echo -en "${yellow}уже существует. ${reset}"
    project_id=$(curl -s "$GITLAB_URL/api/v4/projects?search=$repo" \
      -H "PRIVATE-TOKEN: $ACCESS_TOKEN" | jq -r '.[0].id')
  else
    # Create repository
    response=$(curl -s -X POST "$GITLAB_URL/api/v4/projects" \
      -H "PRIVATE-TOKEN: $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$repo\",\"visibility\":\"private\"}")

    if echo "$response" | grep -q "\"id\""; then
      echo -en "${green}создан. ${reset}"
      project_id=$(echo "$response" | jq -r '.id')
    else
      echo -e "${red}ошибка создания: $response${reset}"
      continue
    fi
  fi

  if [ -z "$project_id" ]; then
    echo -e "${red}❌ Ошибка получения ID проекта${reset}"
    continue
  fi

  # Add webhook
  echo -en "${blue}Добавление webhook:${reset} "
  add_webhook "$project_id"

  # Navigate to local repo directory
  if ! cd "./$repo" 2>/dev/null; then
    echo -e "${red}❌ Не удалось перейти в папку $repo${reset}"
    continue
  fi

  # Setup and push
  setup_and_push "$repo"

  # Return to parent directory
  cd .. || exit 1
done

echo ""
echo -e "${green}✅ Готово!${reset}"
