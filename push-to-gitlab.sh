# !/bin/bash

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


# Display GitLab URL for confirmation
echo "URL: $GITLAB_URL"

# Use token from environment (fallback to input if needed)
ACCESS_TOKEN="$GITLAB_ACCESS_TOKEN"
# if [ -z "$ACCESS_TOKEN" ]; then
#   echo "🔑 Введите личный токен доступа:"
#   read -s ACCESS_TOKEN
# fi

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Токен не введен"
  exit 1
fi

# Validate access token
echo "🔍 Проверяем токен..."
USER_INFO=$(curl -s "$GITLAB_URL/api/v4/user" -H "PRIVATE-TOKEN: $ACCESS_TOKEN")

if echo "$USER_INFO" | grep -q "\"username\""; then
  USERNAME=$(echo "$USER_INFO" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  echo "✅ Токен действителен. Пользователь: $USERNAME"
else
  echo "❌ Неверный токен"
  exit 1
fi

# List of repositories to create and push
REPOSITORIES=(
  "admin-backend"
  "courier-backend"
  "order-backend"
  "admin-frontend"
  "courier-frontend"
  "order-frontend"
  "ci-pipelines"
)

# Prompt for commit message
echo "📝 Введите сообщение для коммита:"
read -r COMMIT_MESSAGE

if [ -z "$COMMIT_MESSAGE" ]; then
  echo "❌ Сообщение для коммита не введено"
  exit 1
fi

echo ""
echo "📁 Обработка ${#REPOSITORIES[@]} репозиториев..."
echo "========================================"

# Function to create repository if it doesn't exist
create_repo() {
  local repo="$1"
  existing=$(curl -s "$GITLAB_URL/api/v4/projects?search=$repo" \
    -H "PRIVATE-TOKEN: $ACCESS_TOKEN" | grep -o "\"path\":\"$repo\"")

  if [ -n "$existing" ]; then
    echo "уже существует"
    return 0
  else
    response=$(curl -s -X POST "$GITLAB_URL/api/v4/projects" \
      -H "PRIVATE-TOKEN: $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$repo\",\"visibility\":\"private\"}")

    if [ $? -eq 0 ] && [ -n "$response" ]; then
      echo "создан"
      return 0
    else
      echo "ошибка создания: $response"
      return 1
    fi
  fi
}

# Function to setup and push local repo
setup_and_push() {
  local repo="$1"

  # Copy .gitignore if it exists
  if [ -f "../.gitignore" ]; then
    cp "../.gitignore" .
  fi

  # Initialize git if not already
  if [ ! -d ".git" ]; then
    git init
    echo "🔄 Инициализирован git в $repo"
  fi

  # Add changes and commit
  git add .
  if ! git commit -m "$COMMIT_MESSAGE"; then
    echo "⚠️ Нет изменений для коммита в $repo"
  fi

  # Set remote if not already set
  git remote add origin "$GITLAB_URL/$USERNAME/$repo.git" 2>/dev/null

  # Push changes
  if git push -u origin master; then
    echo "✅ Успешно запушено в $repo"
  else
    echo "❌ Ошибка пуша в $repo"
    return 1
  fi

  return 0
}

# Process each repository
for repo in "${REPOSITORIES[@]}"; do
  echo -n "• $repo: "

  # Create repo on GitLab
  if ! create_repo "$repo"; then
    continue
  fi

  # Navigate to local repo directory
  if ! cd "./$repo" 2>/dev/null; then
    echo "❌ Не удалось перейти в папку $repo"
    continue
  fi

  # Setup and push
  setup_and_push "$repo"

  # Return to parent directory
  cd .. || exit 1
done

echo ""
echo "✅ Готово!"
