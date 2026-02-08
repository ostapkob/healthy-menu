import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Загружаем .env (если есть)
from dotenv import load_dotenv
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path)

# Добавляем корень проекта (где admin-backend/, order-backend/, courier-backend/)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

config = context.config

# Читаем POSTGRES_DATABASE_URL из shared.database всех сервисов (или .env)
def get_database_url():
    # Пробуем взять из admin-backend (или любого другого)
    try:
        from admin_backend.shared.database import POSTGRES_DATABASE_URL
        return POSTGRES_DATABASE_URL
    except ImportError:
        return os.getenv('POSTGRES_DATABASE_URL')

url = config.get_main_option("sqlalchemy.url")
if url and 'POSTGRES_DATABASE_URL' in url:
    db_url = get_database_url()
    if db_url:
        config.set_main_option("sqlalchemy.url", db_url)
    else:
        raise ValueError("POSTGRES_DATABASE_URL not found in environment variables")

print("---------------------")
print(db_url)
print("---------------------")

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from models import Base  # единый Base из __init__.py

target_metadata = Base.metadata  # один MetaData со всеми таблицами

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

