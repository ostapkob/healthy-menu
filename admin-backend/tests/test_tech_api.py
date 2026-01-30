# tests/test_tech_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
import random
import string

from api.tech import (
    DishTechCreate, DishTechResponse, IngredientInput,
    DishIngredientsUpdate, IngredientTechResponse
)


class TestTechSchemas:
    """Тесты для схем Pydantic из tech.py"""
    
    def test_ingredient_input_schema(self):
        """Тест схемы IngredientInput"""
        data = {
            "food_id": 123,
            "amount_grams": 100.0
        }
        ingredient = IngredientInput(**data)
        assert ingredient.food_id == 123
        assert ingredient.amount_grams == 100.0
        
        with pytest.raises(ValueError) as exc:
            IngredientInput(food_id=123, amount_grams=0)
        assert "greater than 0" in str(exc.value)
    
    def test_dish_tech_create_schema(self):
        """Тест схемы DishTechCreate"""
        data = {
            "name": "Test Dish",
            "ingredients": [
                {"food_id": 1, "amount_grams": 100.0},
                {"food_id": 2, "amount_grams": 50.0}
            ]
        }
        
        dish = DishTechCreate(**data)
        assert dish.name == "Test Dish"
        assert len(dish.ingredients) == 2
    
    def test_ingredient_tech_response_schema(self):
        """Тест схемы IngredientTechResponse"""
        data = {
            "id": 1,
            "food_id": 123,
            "amount_grams": 100.0
        }
        
        ingredient = IngredientTechResponse(**data)
        assert ingredient.id == 1
        assert ingredient.food_id == 123
        assert ingredient.amount_grams == 100.0
    
    def test_dish_tech_response_schema(self):
        """Тест схемы DishTechResponse"""
        data = {
            "id": 1,
            "name": "Test Dish",
            "ingredients": [
                {"id": 1, "food_id": 123, "amount_grams": 100.0},
                {"id": 2, "food_id": 456, "amount_grams": 50.0}
            ]
        }
        
        dish = DishTechResponse(**data)
        assert dish.id == 1
        assert dish.name == "Test Dish"
        assert len(dish.ingredients) == 2


def generate_random_name(length=10):
    """Генерирует случайное имя для блюда"""
    letters = string.ascii_lowercase
    return 'test_' + ''.join(random.choice(letters) for i in range(length))


class TestTechAPI:
    """Тесты для API endpoints из tech.py"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        pass
    
    def test_create_dish_tech_success(self, client: TestClient, db_session: Session, test_foods):
        """Тест успешного создания блюда через tech API"""
        # Генерируем уникальное имя
        dish_name = generate_random_name()
        
        create_data = {
            "name": dish_name,
            "ingredients": [
                {"food_id": 9001, "amount_grams": 200.0},
                {"food_id": 9002, "amount_grams": 150.0}
            ]
        }
        
        response = client.post("/tech/dishes/", json=create_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] is not None
        assert data["name"] == dish_name
        assert len(data["ingredients"]) == 2
        
        food_ids = {ing["food_id"] for ing in data["ingredients"]}
        assert 9001 in food_ids
        assert 9002 in food_ids
        
        # Проверяем, что блюдо создано в базе
        result = db_session.execute(
            text("SELECT * FROM dish WHERE id = :id"),
            {"id": data["id"]}
        ).fetchone()
        
        assert result is not None
        assert result.name == dish_name
        assert float(result.price) == 0.0
    
    def test_create_dish_tech_duplicate_name(self, client: TestClient, db_session: Session, test_foods):
        """Тест создания блюда с существующим именем"""
        dish_name = "Duplicate Test Dish"
        
        # Сначала создаем блюдо напрямую
        db_session.execute(
            text("DELETE FROM dish WHERE name = :name"),
            {"name": dish_name}
        )
        db_session.execute(
            text("INSERT INTO dish (name, price) VALUES (:name, :price)"),
            {"name": dish_name, "price": 10.00}
        )
        db_session.commit()
        
        create_data = {
            "name": dish_name,
            "ingredients": [
                {"food_id": 9001, "amount_grams": 200.0}
            ]
        }
        
        response = client.post("/tech/dishes/", json=create_data)
        assert response.status_code == 400
        assert response.json()["detail"] == "Dish with this name already exists"
    
    def test_create_dish_tech_missing_food(self, client: TestClient, db_session: Session, test_foods):
        """Тест создания блюда с несуществующим продуктом"""
        dish_name = generate_random_name()
        
        create_data = {
            "name": dish_name,
            "ingredients": [
                {"food_id": 9001, "amount_grams": 200.0},
                {"food_id": 999999, "amount_grams": 100.0}  # Несуществующий
            ]
        }
        
        response = client.post("/tech/dishes/", json=create_data)
        assert response.status_code == 400
        detail = response.json()["detail"]
        # Может быть два варианта ошибки
        assert "do not exist" in detail or "Dish with this name already exists" in detail
    
    def test_get_dish_tech_success(self, client: TestClient, db_session: Session, test_foods):
        """Тест успешного получения блюда через tech API"""
        dish_name = generate_random_name()
        
        # Создаем блюдо
        result = db_session.execute(
            text("INSERT INTO dish (name, price) VALUES (:name, :price) RETURNING id"),
            {"name": dish_name, "price": 0.00}
        ).fetchone()
        dish_id = result.id
        
        # Добавляем ингредиенты
        db_session.execute(
            text("""
                INSERT INTO dish_food (dish_id, food_id, amount_grams) 
                VALUES (:dish_id, :food_id, :amount_grams)
            """),
            [
                {"dish_id": dish_id, "food_id": 9001, "amount_grams": 200.0},
                {"dish_id": dish_id, "food_id": 9002, "amount_grams": 150.0}
            ]
        )
        db_session.commit()
        
        response = client.get(f"/tech/dishes/{dish_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == dish_id
        assert data["name"] == dish_name
        assert len(data["ingredients"]) == 2
        
        # Проверяем, что у ингредиентов есть id
        for ingredient in data["ingredients"]:
            assert ingredient["id"] is not None
            assert ingredient["food_id"] in [9001, 9002]
            assert ingredient["amount_grams"] in [200.0, 150.0]
    
    def test_get_dish_tech_not_found(self, client: TestClient, db_session: Session):
        """Тест получения несуществующего блюда"""
        response = client.get("/tech/dishes/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Dish not found"
    
    def test_update_dish_ingredients_success(self, client: TestClient, db_session: Session, test_foods):
        """Тест успешного обновления ингредиентов блюда"""
        dish_name = generate_random_name()
        
        # Создаем блюдо
        result = db_session.execute(
            text("INSERT INTO dish (name, price) VALUES (:name, :price) RETURNING id"),
            {"name": dish_name, "price": 0.00}
        ).fetchone()
        dish_id = result.id
        
        # Начальные ингредиенты
        db_session.execute(
            text("""
                INSERT INTO dish_food (dish_id, food_id, amount_grams) 
                VALUES (:dish_id, :food_id, :amount_grams)
            """),
            {"dish_id": dish_id, "food_id": 9001, "amount_grams": 200.0}
        )
        db_session.commit()
        
        # Обновляем ингредиенты
        update_data = {
            "ingredients": [
                {"food_id": 9002, "amount_grams": 300.0},
                {"food_id": 9003, "amount_grams": 100.0}
            ]
        }
        
        response = client.put(
            f"/tech/dishes/{dish_id}/ingredients",
            json=update_data
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["ingredients"]) == 2
        
        # Проверяем новые ингредиенты
        food_ids = {ing["food_id"] for ing in data["ingredients"]}
        assert 9002 in food_ids
        assert 9003 in food_ids
        
        # Проверяем, что старый ингредиент удален
        old_ingredients = db_session.execute(
            text("SELECT * FROM dish_food WHERE dish_id = :dish_id AND food_id = :food_id"),
            {"dish_id": dish_id, "food_id": 9001}
        ).fetchall()
        
        assert len(old_ingredients) == 0
        
        # Проверяем, что новые ингредиенты созданы
        new_ingredients = db_session.execute(
            text("SELECT * FROM dish_food WHERE dish_id = :dish_id"),
            {"dish_id": dish_id}
        ).fetchall()
        
        assert len(new_ingredients) == 2
    
    def test_update_dish_ingredients_missing_food(self, client: TestClient, db_session: Session, test_foods):
        """Тест обновления ингредиентов с несуществующим продуктом"""
        dish_name = generate_random_name()
        
        # Создаем блюдо
        result = db_session.execute(
            text("INSERT INTO dish (name, price) VALUES (:name, :price) RETURNING id"),
            {"name": dish_name, "price": 0.00}
        ).fetchone()
        dish_id = result.id
        
        update_data = {
            "ingredients": [
                {"food_id": 9001, "amount_grams": 200.0},
                {"food_id": 999999, "amount_grams": 100.0}  # Несуществующий
            ]
        }
        
        response = client.put(
            f"/tech/dishes/{dish_id}/ingredients",
            json=update_data
        )
        
        assert response.status_code == 400
        assert "Some food_ids do not exist" in response.json()["detail"]
    
    def test_update_dish_ingredients_dish_not_found(self, client: TestClient, db_session: Session):
        """Тест обновления ингредиентов несуществующего блюда"""
        update_data = {
            "ingredients": [
                {"food_id": 9001, "amount_grams": 200.0}
            ]
        }
        
        response = client.put(
            "/tech/dishes/999999/ingredients",
            json=update_data
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Dish not found"
    
    def test_delete_dish_tech_success(self, client: TestClient, db_session: Session, test_foods):
        """Тест успешного удаления блюда"""
        dish_name = generate_random_name()
        
        # Создаем блюдо
        result = db_session.execute(
            text("INSERT INTO dish (name, price) VALUES (:name, :price) RETURNING id"),
            {"name": dish_name, "price": 0.00}
        ).fetchone()
        dish_id = result.id
        
        # Добавляем ингредиент
        db_session.execute(
            text("""
                INSERT INTO dish_food (dish_id, food_id, amount_grams) 
                VALUES (:dish_id, :food_id, :amount_grams)
            """),
            {"dish_id": dish_id, "food_id": 9001, "amount_grams": 200.0}
        )
        db_session.commit()
        
        # Удаляем блюдо
        response = client.delete(f"/tech/dishes/{dish_id}")
        assert response.status_code == 200
        assert response.json() == {"ok": True}
        
        # Проверяем, что блюдо удалено
        dish_db = db_session.execute(
            text("SELECT * FROM dish WHERE id = :id"),
            {"id": dish_id}
        ).fetchone()
        
        assert dish_db is None
        
        # Проверяем, что ингредиенты тоже удалены (каскадное удаление)
        ingredients_db = db_session.execute(
            text("SELECT * FROM dish_food WHERE dish_id = :dish_id"),
            {"dish_id": dish_id}
        ).fetchall()
        
        assert len(ingredients_db) == 0
    
    def test_delete_dish_tech_not_found(self, client: TestClient, db_session: Session):
        """Тест удаления несуществующего блюда"""
        response = client.delete("/tech/dishes/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Dish not found"
    
    def test_create_dish_with_empty_ingredients(self, client: TestClient, db_session: Session):
        """Тест создания блюда без ингредиентов"""
        dish_name = generate_random_name()
        
        create_data = {
            "name": dish_name,
            "ingredients": []
        }
        
        response = client.post("/tech/dishes/", json=create_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == dish_name
        assert len(data["ingredients"]) == 0
