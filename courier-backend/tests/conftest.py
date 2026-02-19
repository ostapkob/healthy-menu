import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import asyncio
from typing import Generator

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
from shared.shared_models import Order, OrderItem
from main import app

# Импортируем модели для создания таблиц
from shared.models import Courier, Delivery

# Создаем тестовую модель Order для тестов

# Создаем движок для тестовой базы
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем все таблицы
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session")
def event_loop():
    """Фикстура для event loop"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
def clean_database(db_session: Session):
    """
    Автоматически очищает все таблицы перед каждым тестом.
    """
    # Отключаем триггеры (для ускорения и избежания ошибок)
    db_session.execute(text("SET session_replication_role = 'replica'"))

    # Очищаем каждую таблицу в правильном порядке из-за foreign keys
    tables = ["deliveries", "couriers", "orders"]
    for table in tables:
        db_session.execute(text(f'TRUNCATE TABLE "{table}" CASCADE'))

    # Включаем триггеры обратно
    db_session.execute(text("SET session_replication_role = 'origin'"))

    db_session.commit()
    yield


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для тестовой сессии базы данных"""
    db = TestingSessionLocal()

    # Начинаем транзакцию с использованием savepoint
    db.begin_nested()

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
            print("not connect db")

    # Подменяем зависимость get_db
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


# Фикстуры для создания тестовых данных
@pytest.fixture
def test_courier(db_session: Session):
    """Создает тестового курьера"""
    courier = Courier(
        name="Test Courier",
        status="available",
        photo_url="http://example.com/photo.jpg"
    )
    db_session.add(courier)
    db_session.commit()
    db_session.refresh(courier)
    return courier


@pytest.fixture
def test_order(db_session: Session):
    """Создает тестовый заказ"""
    order = Order(
        user_id=1,
        total_price=100.50,
        status="pending"
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


@pytest.fixture
def test_delivery(db_session: Session, test_courier, test_order):
    """Создает тестовую доставку"""
    delivery = Delivery(
        order_id=test_order.id,
        courier_id=test_courier.id,
        status="assigned"
    )
    db_session.add(delivery)
    db_session.commit()
    db_session.refresh(delivery)
    return delivery
