# Builder стадия: сборка с uv (без dev)
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_NO_DEV=1

WORKDIR /app

# Копируем lock и toml для кэша зависимостей
COPY pyproject.toml ./

# Устанавливаем зависимости без проекта и dev
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project

# Копируем код
COPY . .

# Синхронизируем проект (no-dev, no-editable для продакшена)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

# Runtime стадия: минимальный образ без uv
FROM python:3.13-slim-bookworm

# Создаем пользователя
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app && chown -R appuser:appuser /app

USER appuser
WORKDIR /app

# Копируем venv (активируем через PATH)
COPY --from=builder --chown=appuser:appuser /app/.venv /.venv
COPY --from=builder --chown=appuser:appuser /app /app

ENV PATH="/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1


EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Используем gunicorn для продакшена
# CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "main:app", "--bind", "0.0.0.0:8000"]
