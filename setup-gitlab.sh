#!/bin/bash

set -o allexport
source ./backend/.env
set +o allexport

echo $GITLAB_URL
echo "🔑 Введите личный токен доступа ostapkob:"
read -s ACCESS_TOKEN
echo ""

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Токен не введен"
  exit 1
fi

echo "🔍 Проверяем токен..."
USER_INFO=$(curl -s "$GITLAB_URL/api/v4/user" \
  -H "PRIVATE-TOKEN: $ACCESS_TOKEN")

if echo "$USER_INFO" | grep -q "\"username\""; then
  USERNAME=$(echo "$USER_INFO" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
  echo "✅ Токен действителен. Пользователь: $USERNAME"
else
  echo "❌ Неверный токен"
  exit 1
fi

REPOSITORIES=(
    "backend-admin"
    "backend-courier" 
    "backend-order"
    "frontend-admin"
    "frontend-courier"
    "frontend-order"
)

echo ""
echo "📁 Создаем ${#REPOSITORIES[@]} репозиториев..."
echo "========================================"

for repo in "${REPOSITORIES[@]}"; do
  echo -n "• $repo: "
  
  # Проверяем, существует ли уже репозиторий
  existing=$(curl -s "$GITLAB_URL/api/v4/projects?search=$repo" \
    -H "PRIVATE-TOKEN: $ACCESS_TOKEN" | grep -o "\"path\":\"$repo\"")
  
  if [ -n "$existing" ]; then
    echo "уже существует"
  else
    # Создаем репозиторий
    curl -s -X POST "$GITLAB_URL/api/v4/projects" \
      -H "PRIVATE-TOKEN: $ACCESS_TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"name\":\"$repo\",\"visibility\":\"private\"}" > /dev/null
    
    if [ $? -eq 0 ]; then
      echo "создан"
    else
      echo "ошибка"
    fi
  fi
done

echo ""
echo "✅ Готово!"
