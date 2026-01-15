# Первая стадия: сборка зависимостей и общих модулей
FROM python:3.11-slim AS builder_order

WORKDIR /app

# Копируем общие зависимости
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Вторая стадия: финальный образ
FROM python:3.11-slim

# Копируем установленные зависимости из стадии builder
COPY --from=builder_order /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder_order /usr/local/bin /usr/local/bin

# Копируем код приложения
COPY ./order /app

# Настройки Python
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Создаем пользователя и меняем владельца
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

WORKDIR /app

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Используем gunicorn для продакшена
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
