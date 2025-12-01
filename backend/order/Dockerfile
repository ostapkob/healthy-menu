# Первая стадия: сборка зависимостей и общих модулей
FROM python:3.11-slim AS builder

WORKDIR /app

# Копируем общие зависимости
COPY ./shared/requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Копируем общие модули
COPY ./shared/ /app/shared/

# Устанавливаем PYTHONPATH для импортов
ENV PYTHONPATH=/app

# Вторая стадия: финальный образ для запуска
FROM python:3.11-slim

# Копируем установленные зависимости из стадии builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Копируем общие модули
COPY --from=builder /app/shared /app/shared

# Устанавливаем PYTHONPATH для импортов
ENV PYTHONPATH=/app

# Копируем код приложения
COPY ./order /app

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
