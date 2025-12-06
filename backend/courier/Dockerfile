# Первая стадия: сборка зависимостей и общих модулей
FROM python:3.11-slim AS builder_courier

WORKDIR /app

# Копируем общие зависимости
COPY ./shared/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем общие модули
COPY ./shared/ /app/shared/

# Вторая стадия: финальный образ для запуска
FROM python:3.11-slim

# Копируем установленные зависимости из стадии builder
COPY --from=builder_courier /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder_courier /usr/local/bin /usr/local/bin

# Копируем общие модули
COPY --from=builder_courier /app/shared /app/shared

# Копируем код приложения
COPY ./courier /app

# Настройки Python
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser


WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Используем gunicorn для продакшена
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]

