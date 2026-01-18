#!/bin/bash

# Создаем папку для объединенных моделей
mkdir -p migrations/models

# Копируем модели из всех сервисов
cp admin-backend/shared/database.py migrations/models/database.py
cp admin-backend/shared/models.py migrations/models/admin_models.py
cp order-backend/shared/models.py migrations/models/order_models.py
cp courier-backend/shared/models.py migrations/models/courier_models.py

echo "Модели скопированы в migrations/models/"

sed -i 's/from shared.database import Base/from . import Base/g' migrations/models/admin_models.py
sed -i '/shared_models/d' migrations/models/admin_models.py

sed -i 's/from shared.database import Base/from . import Base/g' migrations/models/order_models.py
sed -i '/shared_models/d' migrations/models/order_models.py

sed -i 's/from shared.database import Base/from . import Base/g' migrations/models/courier_models.py
sed -i '/shared_models/d' migrations/models/courier_models.py

echo "Импорты исправлены!"


cat << EOF >  migrations/models/__init__.py
from .database import Base
from . import admin_models, order_models, courier_models

__all__ = ['Base', 'admin_models', 'order_models', 'courier_models']
EOF

echo "__init__.py готов"

cd migrations
uv run alembic revision --autogenerate -m "init schemas"
uv run alembic upgrade head
echo "alembic готов"
