# tests/conftest.py (для order-backend)
import pytest
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import uuid
import random

# Настройки тестовой базы данных для order сервиса
TEST_DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
TEST_DB_PORT = os.getenv("POSTGRES_PORT", "5432")
TEST_DB_NAME = os.getenv("POSTGRES_TESTS_DB", "food_db_tests")
TEST_DB_USER = os.getenv("POSTGRES_TESTS_USER", "postgres")
TEST_DB_PASSWORD = os.getenv("POSTGRES_TEST_PASSWORD", "postgres")

TEST_DATABASE_URL = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASSWORD}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}"

# Импортируем order app
from main import app as order_app
from shared.database import get_db

# Создаем движок для тестовой базы
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


def generate_unique_name(prefix="test"):
    """Генерирует уникальное имя для тестовых данных"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}_{random.randint(1000, 9999)}"


@pytest.fixture(scope="function")
def db_session():
    """Фикстура для тестовой сессии базы данных"""
    db = TestingSessionLocal()

    # Начинаем вложенную транзакцию
    db.begin_nested()

    try:
        yield db
    finally:
        # Откатываем все изменения, сделанные в тесте
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def order_client(db_session: Session):
    """Фикстура для тестового клиента Order сервиса"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Подменяем зависимость get_db
    order_app.dependency_overrides[get_db] = override_get_db

    with TestClient(order_app) as test_client:
        yield test_client

    # Очищаем переопределения после теста
    order_app.dependency_overrides.clear()


@pytest.fixture
def mock_kafka_producer():
    """Фикстура для мока Kafka producer"""
    with patch('core.kafka.get_kafka_producer') as mock_producer:
        mock_instance = MagicMock()
        mock_instance.produce = MagicMock()
        mock_instance.poll = MagicMock()
        mock_instance.flush = MagicMock()
        mock_producer.return_value = mock_instance
        yield mock_producer


@pytest.fixture
def test_dish(db_session: Session):
    """Создает тестовое блюдо"""
    # Генерируем уникальное имя
    dish_name = generate_unique_name("test_dish")

    # Создаем блюдо
    dish = db_session.execute(
        text("""
            INSERT INTO dish (name, price, description, image_url)
            VALUES (:name, :price, :description, :image_url)
            RETURNING id, name, price, description, image_url
        """),
        {
            "name": dish_name,
            "price": 12.99,
            "description": "Test description",
            "image_url": "http://example.com/test.jpg"
        }
    ).fetchone()

    db_session.commit()
    return dish


@pytest.fixture
def test_nutrients(db_session: Session):
    """Создает тестовые нутриенты"""
    # Используем безопасный подход: создаем только если не существует
    nutrients_data = [
        (1003, "Protein", "G", "Белок", 50.0),
        (1004, "Total lipid (fat)", "G", "Жиры", 70.0),
        (1005, "Carbohydrate, by difference", "G", "Углеводы", 300.0),
        (1008, "Energy", "KCAL", "Энергия", 2000.0),
    ]

    created_nutrients = []

    for nutrient_id, name_en, unit_name, name_ru, daily_norm in nutrients_data:
        # Проверяем существование нутриента
        nutrient = db_session.execute(
            text("SELECT * FROM nutrient WHERE id = :id"),
            {"id": nutrient_id}
        ).fetchone()

        if not nutrient:
            # Создаем нутриент
            nutrient = db_session.execute(
                text("""
                    INSERT INTO nutrient (id, name, unit_name, nutrient_nbr)
                    VALUES (:id, :name, :unit_name, :nutrient_nbr)
                    RETURNING id, name, unit_name
                """),
                {
                    "id": nutrient_id,
                    "name": name_en,
                    "unit_name": unit_name,
                    "nutrient_nbr": float(nutrient_id)
                }
            ).fetchone()

        # Проверяем существование перевода
        translation = db_session.execute(
            text("SELECT * FROM nutrient_ru WHERE nutrient_id = :nutrient_id"),
            {"nutrient_id": nutrient_id}
        ).fetchone()

        if not translation:
            # Создаем русский перевод
            db_session.execute(
                text("""
                    INSERT INTO nutrient_ru (nutrient_id, name_ru)
                    VALUES (:nutrient_id, :name_ru)
                """),
                {"nutrient_id": nutrient_id, "name_ru": name_ru}
            )

        # Проверяем существование суточной нормы
        norm = db_session.execute(
            text("SELECT * FROM daily_norms WHERE nutrient_id = :nutrient_id"),
            {"nutrient_id": nutrient_id}
        ).fetchone()

        if not norm:
            # Создаем суточную норму
            db_session.execute(
                text("""
                    INSERT INTO daily_norms (nutrient_id, amount, unit_name, source)
                    VALUES (:nutrient_id, :amount, :unit_name, :source)
                """),
                {
                    "nutrient_id": nutrient_id,
                    "amount": daily_norm,
                    "unit_name": unit_name,
                    "source": "test"
                }
            )

        created_nutrients.append(nutrient_id)

    db_session.commit()
    return created_nutrients


@pytest.fixture
def test_food(db_session: Session):
    """Создает тестовый продукт"""
    # Генерируем уникальное описание
    food_desc = generate_unique_name("test_food")

    # Находим или создаем тестовую категорию
    category = db_session.execute(
        text("SELECT id FROM food_category WHERE code = 'TEST'")
    ).fetchone()

    if not category:
        category = db_session.execute(
            text("""
                INSERT INTO food_category (code, description)
                VALUES ('TEST', 'Test Category')
                RETURNING id
            """)
        ).fetchone()

    # Находим максимальный fdc_id и создаем уникальный
    max_fdc = db_session.execute(
        text("SELECT COALESCE(MAX(fdc_id), 0) FROM food")
    ).fetchone()[0]

    fdc_id = max_fdc + 1

    # Создаем продукт
    food = db_session.execute(
        text("""
            INSERT INTO food (fdc_id, description, food_category_id)
            VALUES (:fdc_id, :description, :category_id)
            RETURNING fdc_id, description
        """),
        {
            "fdc_id": fdc_id,
            "description": food_desc,
            "category_id": category.id
        }
    ).fetchone()

    db_session.commit()
    return food


@pytest.fixture
def test_food_nutrients(db_session: Session, test_food, test_nutrients):
    """Создает тестовые нутриенты для продукта"""
    # Добавляем нутриенты к продукту
    nutrients_data = [
        (1003, 20.0),  # Белок, 20г на 100г продукта
        (1004, 10.0),  # Жиры, 10г
        (1005, 60.0),  # Углеводы, 60г
        (1008, 400.0), # Энергия, 400 ккал
    ]

    for nutrient_id, amount in nutrients_data:
        # Удаляем старую запись если есть
        db_session.execute(
            text("DELETE FROM food_nutrient WHERE fdc_id = :fdc_id AND nutrient_id = :nutrient_id"),
            {"fdc_id": test_food.fdc_id, "nutrient_id": nutrient_id}
        )

        db_session.execute(
            text("""
                INSERT INTO food_nutrient (fdc_id, nutrient_id, amount, data_points)
                VALUES (:fdc_id, :nutrient_id, :amount, :data_points)
            """),
            {
                "fdc_id": test_food.fdc_id,
                "nutrient_id": nutrient_id,
                "amount": amount,
                "data_points": 1
            }
        )

    db_session.commit()


@pytest.fixture
def test_dish_food(db_session: Session, test_dish, test_food):
    """Создает тестовую связь блюдо-продукт"""
    # Создаем связь
    dish_food = db_session.execute(
        text("""
            INSERT INTO dish_food (dish_id, food_id, amount_grams)
            VALUES (:dish_id, :food_id, :amount_grams)
            RETURNING id, dish_id, food_id, amount_grams
        """),
        {
            "dish_id": test_dish.id,
            "food_id": test_food.fdc_id,
            "amount_grams": 250.0  # 250г продукта в блюде
        }
    ).fetchone()

    db_session.commit()
    return dish_food


@pytest.fixture
def test_order(db_session: Session):
    """Создает тестовый заказ"""
    order = db_session.execute(
        text("""
            INSERT INTO orders (user_id, status, total_price)
            VALUES (:user_id, :status, :total_price)
            RETURNING id, user_id, status, total_price, created_at
        """),
        {
            "user_id": random.randint(1000, 9999),  # Уникальный user_id
            "status": "pending",
            "total_price": 25.98
        }
    ).fetchone()

    db_session.commit()
    return order


@pytest.fixture
def test_order_items(db_session: Session, test_order, test_dish):
    """Создает тестовые позиции заказа"""
    # Создаем позиции
    items = []
    for i in range(2):
        item = db_session.execute(
            text("""
                INSERT INTO order_items (order_id, dish_id, quantity, price)
                VALUES (:order_id, :dish_id, :quantity, :price)
                RETURNING id, order_id, dish_id, quantity, price
            """),
            {
                "order_id": test_order.id,
                "dish_id": test_dish.id,
                "quantity": 1,
                "price": 12.99
            }
        ).fetchone()
        items.append(item)

    db_session.commit()
    return items


@pytest.fixture
def test_order_with_items(db_session: Session):
    """Комбинированная фикстура: заказ с позициями и блюдом"""
    # Создаем блюдо
    dish_name = generate_unique_name("dish_for_order")
    dish = db_session.execute(
        text("""
            INSERT INTO dish (name, price)
            VALUES (:name, :price)
            RETURNING id, name, price
        """),
        {"name": dish_name, "price": 15.99}
    ).fetchone()

    # Создаем заказ
    order = db_session.execute(
        text("""
            INSERT INTO orders (user_id, status, total_price)
            VALUES (:user_id, :status, :total_price)
            RETURNING id, user_id, status, total_price, created_at
        """),
        {
            "user_id": random.randint(1000, 9999),
            "status": "pending",
            "total_price": 31.98  # 15.99 * 2
        }
    ).fetchone()

    # Создаем позиции
    items = []
    for i in range(2):
        item = db_session.execute(
            text("""
                INSERT INTO order_items (order_id, dish_id, quantity, price)
                VALUES (:order_id, :dish_id, :quantity, :price)
                RETURNING id, order_id, dish_id, quantity, price
            """),
            {
                "order_id": order.id,
                "dish_id": dish.id,
                "quantity": 1,
                "price": 15.99
            }
        ).fetchone()
        items.append(item)

    db_session.commit()

    return {
        "order": order,
        "items": items,
        "dish": dish
    }
