# tests/test_dishes_api.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal

from shared.models import Dish
from api.dishes import DishAdminListItem, DishAdminDetail, DishAdminUpdate


class TestDishAdminSchemas:
    """Тесты для схем Pydantic из dishes.py"""
    
    def test_dish_admin_list_item_schema(self):
        """Тест схемы DishAdminListItem"""
        data = {
            "id": 1,
            "name": "Test Dish",
            "price": 12.99,
            "description": "Test description",
            "image_url": "http://example.com/image.jpg"
        }
        
        item = DishAdminListItem(**data)
        assert item.id == 1
        assert item.name == "Test Dish"
        assert item.price == 12.99
        assert item.description == "Test description"
        assert item.image_url == "http://example.com/image.jpg"
        
        data_minimal = {
            "id": 2,
            "name": "Test Dish 2",
            "price": 9.99,
            "description": None,
            "image_url": None
        }
        item2 = DishAdminListItem(**data_minimal)
        assert item2.description is None
        assert item2.image_url is None
    
    def test_dish_admin_detail_schema(self):
        """Тест схемы DishAdminDetail (наследуется от DishAdminListItem)"""
        data = {
            "id": 1,
            "name": "Test Dish",
            "price": 12.99,
            "description": "Test description",
            "image_url": "http://example.com/image.jpg"
        }
        
        item = DishAdminDetail(**data)
        assert item.id == 1
        assert item.name == "Test Dish"
    
    def test_dish_admin_update_schema(self):
        """Тест схемы DishAdminUpdate"""
        from pydantic import ValidationError
        
        data_empty = {}
        update = DishAdminUpdate(**data_empty)
        assert update.price is None
        assert update.description is None
        assert update.image_url is None
        
        data_partial = {
            "price": 15.99,
            "description": "Updated description"
        }
        update2 = DishAdminUpdate(**data_partial)
        assert update2.price == 15.99
        assert update2.description == "Updated description"
        assert update2.image_url is None
        
        with pytest.raises(ValidationError) as exc:
            DishAdminUpdate(price=-1.0)
        assert "greater_than_equal" in str(exc.value)


class TestDishAdminAPI:
    """Тесты для API endpoints из dishes.py"""
    
    def test_list_dishes_empty(self, client: TestClient, db_session: Session):
        """Тест получения пустого списка блюд"""
        # Очищаем таблицу dish перед тестом
        db_session.execute(text("DELETE FROM dish"))
        db_session.commit()
        
        response = client.get("/dishes/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_list_dishes_with_data(self, client: TestClient, db_session: Session):
        """Тест получения списка блюд с данными"""
        # Очищаем таблицу dish перед тестом
        db_session.execute(text("DELETE FROM dish"))
        db_session.commit()
        
        # Создаем тестовые блюда через модель
        dish1 = Dish(
            name="Pasta Carbonara",
            price=Decimal("12.50"),
            description="Creamy pasta with bacon",
            image_url="http://example.com/pasta.jpg"
        )
        dish2 = Dish(
            name="Caesar Salad",
            price=Decimal("8.99"),
            description=None,
            image_url=None
        )
        
        db_session.add_all([dish1, dish2])
        db_session.commit()
        
        response = client.get("/dishes/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        
        # Сортируем по имени для надежности
        sorted_data = sorted(data, key=lambda x: x["name"])
        assert sorted_data[0]["name"] == "Caesar Salad"
        assert sorted_data[0]["price"] == 8.99
        assert sorted_data[1]["name"] == "Pasta Carbonara"
        assert sorted_data[1]["price"] == 12.5
    
    def test_get_dish_admin_success(self, client: TestClient, db_session: Session):
        """Тест успешного получения деталей блюда"""
        # Очищаем таблицу dish перед тестом
        db_session.execute(text("DELETE FROM dish"))
        db_session.commit()
        
        dish = Dish(
            name="Test Dish",
            price=Decimal("10.00"),
            description="Test description",
            image_url="http://example.com/test.jpg"
        )
        db_session.add(dish)
        db_session.commit()
        
        response = client.get(f"/dishes/{dish.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == dish.id
        assert data["name"] == "Test Dish"
        assert data["price"] == 10.0
        assert data["description"] == "Test description"
        assert data["image_url"] == "http://example.com/test.jpg"
    
    def test_get_dish_admin_not_found(self, client: TestClient, db_session: Session):
        """Тест получения несуществующего блюда"""
        response = client.get("/dishes/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Dish not found"
    
    def test_update_dish_admin_success(self, client: TestClient, db_session: Session):
        """Тест успешного обновления блюда"""
        # Очищаем таблицу dish перед тестом
        db_session.execute(text("DELETE FROM dish"))
        db_session.commit()
        
        dish = Dish(
            name="Original Dish",
            price=Decimal("10.00"),
            description="Original description",
            image_url="http://example.com/original.jpg"
        )
        db_session.add(dish)
        db_session.commit()
        
        update_data = {
            "price": 15.99,
            "description": "Updated description",
            "image_url": "http://example.com/updated.jpg"
        }
        
        response = client.put(
            f"/dishes/{dish.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["price"] == 15.99
        assert data["description"] == "Updated description"
        assert data["image_url"] == "http://example.com/updated.jpg"
        assert data["name"] == "Original Dish"
        
        # Проверяем, что в базе обновилось
        db_session.refresh(dish)
        assert float(dish.price) == 15.99
        assert dish.description == "Updated description"
    
    def test_update_dish_admin_partial(self, client: TestClient, db_session: Session):
        """Тест частичного обновления блюда"""
        # Очищаем таблицу dish перед тестом
        db_session.execute(text("DELETE FROM dish"))
        db_session.commit()
        
        dish = Dish(
            name="Test Dish",
            price=Decimal("10.00"),
            description="Original description",
            image_url="http://example.com/original.jpg"
        )
        db_session.add(dish)
        db_session.commit()
        
        update_data = {"price": 12.50}
        
        response = client.put(
            f"/dishes/{dish.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["price"] == 12.50
        assert data["description"] == "Original description"
        assert data["image_url"] == "http://example.com/original.jpg"
    
    def test_update_dish_admin_not_found(self, client: TestClient, db_session: Session):
        """Тест обновления несуществующего блюда"""
        update_data = {"price": 15.99}
        
        response = client.put(
            "/dishes/999999",
            json=update_data
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Dish not found"
    
    def test_update_dish_admin_negative_price(self, client: TestClient, db_session: Session):
        """Тест обновления с отрицательной ценой"""
        # Очищаем таблицу dish перед тестом
        db_session.execute(text("DELETE FROM dish"))
        db_session.commit()
        
        dish = Dish(
            name="Test Dish",
            price=Decimal("10.00"),
            description="Test",
            image_url=None
        )
        db_session.add(dish)
        db_session.commit()
        
        update_data = {"price": -5.00}
        
        response = client.put(
            f"/dishes/{dish.id}",
            json=update_data
        )
        
        assert response.status_code == 422
