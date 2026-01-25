# tests/conftest.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Настройки тестовой базы данных
TEST_DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
TEST_DB_PORT = os.getenv("POSTGRES_PORT", "5432")
TEST_DB_NAME = os.getenv("POSTGRES_TESTS_DB", "food_db_tests")
TEST_DB_USER = os.getenv("POSTGRES_TESTS_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD", "postgres")

# Строка подключения
TEST_DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

# Импортируем все необходимое
from shared.database import Base, get_db
from api.dishes import router as dishes_router
from api.tech import router as tech_router

# Создаем движок для тестовой базы
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем тестовое приложение
app = FastAPI()
app.include_router(dishes_router)
app.include_router(tech_router)


@pytest.fixture(scope="function", autouse=True)
def clean_database(db_session: Session):
    """
    Автоматически очищает все таблицы перед каждым тестом.
    autouse=True означает, что фикстура запускается для каждого теста автоматически.
    """
    # Получаем список всех таблиц
    tables = db_session.execute(text("""
        SELECT tablename 
        FROM pg_tables 
        WHERE schemaname = 'public'
          AND tablename NOT LIKE 'pg_%'
          AND tablename NOT LIKE 'sql_%'
    """)).fetchall()
    
    # Отключаем триггеры (для ускорения и избежания ошибок)
    db_session.execute(text("SET session_replication_role = 'replica'"))
    
    # Очищаем каждую таблицу
    for table in tables:
        db_session.execute(text(f'TRUNCATE TABLE "{table[0]}" CASCADE'))
    
    # Включаем триггеры обратно
    db_session.execute(text("SET session_replication_role = 'origin'"))
    
    db_session.commit()
    
    yield

@pytest.fixture(scope="function")
def db_session():
    """Фикстура для тестовой сессии базы данных"""
    db = TestingSessionLocal()
    
    # Начинаем транзакцию с использованием savepoint
    db.begin_nested()  # Используем вложенную транзакцию
    
    try:
        yield db
    finally:
        # Откатываем все изменения, сделанные в тесте
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """Фикстура для тестового клиента FastAPI"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Подменяем зависимость get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


# Фикстура для создания тестовых данных
@pytest.fixture
def test_category(db_session: Session):
    """Создает тестовую категорию продуктов"""
    # Используем savepoint внутри фикстуры
    db_session.begin_nested()
    
    # Проверяем, существует ли уже категория с таким id
    category = db_session.execute(
        text("SELECT * FROM food_category WHERE id = :id FOR UPDATE"),
        {"id": 9999}
    ).fetchone()
    
    if not category:
        category = db_session.execute(
            text("""
                INSERT INTO food_category (id, code, description) 
                VALUES (:id, :code, :description)
                RETURNING *
            """),
            {"id": 9999, "code": "TEST", "description": "Test Category"}
        ).fetchone()
        db_session.commit()
    
    return category


@pytest.fixture
def test_foods(db_session: Session, test_category):
    """Создает тестовые продукты"""
    # Удаляем старые тестовые продукты если есть
    db_session.execute(
        text("DELETE FROM food WHERE fdc_id BETWEEN :start AND :end"),
        {"start": 9000, "end": 9010}
    )
    
    # Создаем новые тестовые продукты
    foods = []
    for i in range(1, 6):
        food = db_session.execute(
            text("""
                INSERT INTO food (fdc_id, description, food_category_id)
                VALUES (:fdc_id, :description, :food_category_id)
                RETURNING *
            """),
            {
                "fdc_id": 9000 + i,
                "description": f"Test Food {i}",
                "food_category_id": test_category.id
            }
        ).fetchone()
        foods.append(food)
    
    db_session.commit()
    return foods
