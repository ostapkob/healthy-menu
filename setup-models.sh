#!/bin/bash

# Создаем папку для объединенных моделей
mkdir -p migrations/models

# Копируем модели из всех сервисов
cp admin-backend/shared/models.py migrations/models/admin_models.py
cp order-backend/shared/models.py migrations/models/order_models.py
cp courier-backend/shared/models.py migrations/models/courier_models.py

# Создаем __init__.py для папки models
echo "" > migrations/models/__init__.py

echo "Модели скопированы в migrations/models/"

# Исправляем импорты в admin_models.py
sed -i 's/from shared.database import Base/from .database import Base/g' migrations/models/admin_models.py

# Исправляем импорты в order_models.py
sed -i 's/from shared.database import Base/from .database import Base/g' migrations/models/order_models.py

# Исправляем импорты в courier_models.py
sed -i 's/from shared.database import Base/from .database import Base/g' migrations/models/courier_models.py

echo "Импорты исправлены!"
