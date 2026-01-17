#!/bin/bash

set -o allexport
source ./backend/.env
set +o allexport

echo $GITLAB_URL
echo "🔑 Введите личный токен доступа:"
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
    "admin-backend"
    "courier-backend" 
    "order-backend"
    "admin-frontend"
    "courier-frontend"
    "order-frontend"
)

# Запрашиваем сообщение для коммита
echo "📝 Введите сообщение для коммита:"
read COMMIT_MESSAGE

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
      continue
    fi
  fi

  # Переходим в папку репозитория
  cd "./$repo" || { echo "❌ Не удалось перейти в папку $repo"; continue; }

  # Проверяем, инициализирован ли git
  if [ ! -d ".git" ]; then
    git init
    echo "🔄 Инициализирован git в $repo"
  fi

  # Добавляем изменения, коммитим и пушим
  git add .
  git commit -m "$COMMIT_MESSAGE" || { echo "⚠️ Нет изменений для коммита в $repo"; }
  
  # Настраиваем удаленный репозиторий, если не настроен
  git remote add origin "$GITLAB_URL/$USERNAME/$repo.git" 2>/dev/null
  
  # Пушим изменения
  git push -u origin master
  
  # Возвращаемся в предыдущую директорию
  cd - || exit
done

echo ""
echo "✅ Готово!"

