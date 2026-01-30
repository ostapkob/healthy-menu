# tests/test_db.py (исправленная версия)
import pytest
from pydantic import ValidationError
from decimal import Decimal
import sys
import os

# Добавляем родительскую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import (
    NutrientInfo,
    DishNutrientsResponse,
    OrderNutrientsResponse,
    UserNutrientsResponse,
    MenuMacros,
    MenuMicronutrient,
    MenuDish,
    DishResponse,
    OrderItemCreate,
    OrderItemResponse,
    OrderCreate,
    OrderResponse
)


class TestNutrientInfoSchema:
    """Тесты для схемы NutrientInfo"""
    
    def test_nutrient_info_creation(self):
        """Тест создания NutrientInfo с полными данными"""
        data = {
            "name": "Белок",
            "unit_name": "г",
            "amount": 25,
            "daily_percentage": 50
        }
        
        nutrient = NutrientInfo(**data)
        assert nutrient.name == "Белок"
        assert nutrient.unit_name == "г"
        assert nutrient.amount == 25
        assert nutrient.daily_percentage == 50
    
    def test_nutrient_info_without_percentage(self):
        """Тест создания NutrientInfo без daily_percentage"""
        data = {
            "name": "Жиры",
            "unit_name": "г",
            "amount": 15
        }
        
        nutrient = NutrientInfo(**data)
        assert nutrient.daily_percentage is None


class TestDishNutrientsResponseSchema:
    """Тесты для схемы DishNutrientsResponse"""
    
    def test_dish_nutrients_response_creation(self):
        """Тест создания DishNutrientsResponse"""
        data = {
            "dish_id": 1,
            "dish_name": "Паста Карбонара",
            "total_weight_g": 350.5,
            "nutrients": {
                "1003": {
                    "name": "Белок",
                    "unit_name": "г",
                    "amount": 25,
                    "daily_percentage": 50
                }
            }
        }
        
        response = DishNutrientsResponse(**data)
        assert response.dish_id == 1
        assert response.dish_name == "Паста Карбонара"
        assert response.total_weight_g == 350.5
        assert "1003" in response.nutrients
        assert response.nutrients["1003"].name == "Белок"


class TestOrderNutrientsResponseSchema:
    """Тесты для схемы OrderNutrientsResponse"""
    
    def test_order_nutrients_response_creation(self):
        """Тест создания OrderNutrientsResponse"""
        data = {
            "order_id": 123,
            "total_nutrients": {
                "1003": {
                    "name": "Белок",
                    "unit_name": "г",
                    "amount": 50,
                    "daily_percentage": 100
                }
            },
            "dishes": [
                {
                    "dish_id": 1,
                    "dish_name": "Паста",
                    "total_weight_g": 350.0,
                    "nutrients": {
                        "1003": {
                            "name": "Белок",
                            "unit_name": "г",
                            "amount": 25,
                            "daily_percentage": 50
                        }
                    }
                }
            ]
        }
        
        response = OrderNutrientsResponse(**data)
        assert response.order_id == 123
        assert len(response.total_nutrients) == 1
        assert len(response.dishes) == 1
        assert response.dishes[0].dish_id == 1


class TestUserNutrientsResponseSchema:
    """Тесты для схемы UserNutrientsResponse"""
    
    def test_user_nutrients_response_creation(self):
        """Тест создания UserNutrientsResponse"""
        data = {
            "user_id": 1,
            "total_nutrients": {
                "1003": {
                    "name": "Белок",
                    "unit_name": "г",
                    "amount": 150,
                    "daily_percentage": 300
                }
            },
            "order_count": 3
        }
        
        response = UserNutrientsResponse(**data)
        assert response.user_id == 1
        assert response.order_count == 3
        assert "1003" in response.total_nutrients


class TestMenuMacrosSchema:
    """Тесты для схемы MenuMacros"""
    
    def test_menu_macros_creation(self):
        """Тест создания MenuMacros"""
        data = {
            "calories": 450,
            "protein": 25,
            "fat": 15,
            "carbs": 50
        }
        
        macros = MenuMacros(**data)
        assert macros.calories == 450
        assert macros.protein == 25
        assert macros.fat == 15
        assert macros.carbs == 50
    
    def test_menu_macros_validation(self):
        """Тест валидации MenuMacros"""
        # Все поля обязательны - должно вызвать ошибку
        with pytest.raises(ValidationError):
            MenuMacros(calories=450, protein=25, fat=15)  # Нет carbs
        
        # Отрицательные значения не принимаются
        with pytest.raises(ValidationError):
            MenuMacros(calories=-100, protein=25, fat=15, carbs=50)
        
        # Строки, которые не конвертируются в числа, не принимаются
        with pytest.raises(ValidationError):
            MenuMacros(calories="не число", protein=25, fat=15, carbs=50)



class TestMenuMicronutrientSchema:
    """Тесты для схемы MenuMicronutrient"""
    
    def test_menu_micronutrient_creation(self):
        """Тест создания MenuMicronutrient"""
        data = {
            "name": "Кальций",
            "unit": "мг",
            "value": 150,
            "coverage_percent": 15
        }
        
        micronutrient = MenuMicronutrient(**data)
        assert micronutrient.name == "Кальций"
        assert micronutrient.unit == "мг"
        assert micronutrient.value == 150
        assert micronutrient.coverage_percent == 15


class TestMenuDishSchema:
    """Тесты для схемы MenuDish"""
    
    def test_menu_dish_creation(self):
        """Тест создания MenuDish с полными данными"""
        data = {
            "id": 1,
            "name": "Паста Карбонара",
            "price": 12.99,
            "description": "Вкусная паста",
            "macros": {
                "calories": 450,
                "protein": 25,
                "fat": 15,
                "carbs": 50
            },
            "micronutrients": {
                "1008": {
                    "name": "Кальций",
                    "unit": "мг",
                    "value": 150,
                    "coverage_percent": 15
                }
            },
            "recommendations": ["Богато белком"],
            "score": 8,
            "image_url": "http://example.com/pasta.jpg"
        }
        
        dish = MenuDish(**data)
        assert dish.id == 1
        assert dish.name == "Паста Карбонара"
        assert dish.price == 12.99
        assert dish.description == "Вкусная паста"
        assert dish.macros.calories == 450
        assert len(dish.micronutrients) == 1
        assert len(dish.recommendations) == 1
        assert dish.score == 8
        assert dish.image_url == "http://example.com/pasta.jpg"
    
    def test_menu_dish_minimal(self):
        """Тест создания MenuDish с минимальными данными"""
        data = {
            "id": 2,
            "name": "Салат",
            "price": 8.99,
            "macros": {
                "calories": 200,
                "protein": 10,
                "fat": 5,
                "carbs": 25
            },
            "micronutrients": {},
            "recommendations": []
        }
        
        dish = MenuDish(**data)
        assert dish.description is None
        assert dish.score is None
        assert dish.image_url is None


class TestDishResponseSchema:
    """Тесты для схемы DishResponse"""
    
    def test_dish_response_creation(self):
        """Тест создания DishResponse"""
        data = {
            "id": 1,
            "name": "Паста",
            "price": 12.99
        }
        
        dish = DishResponse(**data)
        assert dish.id == 1
        assert dish.name == "Паста"
        assert dish.price == 12.99


class TestOrderItemCreateSchema:
    """Тесты для схемы OrderItemCreate"""
    
    def test_order_item_create_creation(self):
        """Тест создания OrderItemCreate"""
        data = {
            "dish_id": 1,
            "quantity": 2
        }
        
        item = OrderItemCreate(**data)
        assert item.dish_id == 1
        assert item.quantity == 2
    
    def test_order_item_create_validation(self):
        """Тест валидации OrderItemCreate"""
        # dish_id обязателен
        with pytest.raises(ValidationError):
            OrderItemCreate(quantity=1)
        
        # quantity обязателен
        with pytest.raises(ValidationError):
            OrderItemCreate(dish_id=1)
        
        # quantity должно быть больше 0
        with pytest.raises(ValidationError):
            OrderItemCreate(dish_id=1, quantity=0)
        
        with pytest.raises(ValidationError):
            OrderItemCreate(dish_id=1, quantity=-1)
        
        # Нечисловые значения не принимаются
        with pytest.raises(ValidationError):
            OrderItemCreate(dish_id=1, quantity="два")


class TestOrderItemResponseSchema:
    """Тесты для схемы OrderItemResponse"""
    
    def test_order_item_response_creation(self):
        """Тест создания OrderItemResponse"""
        data = {
            "id": 1,
            "dish_id": 5,
            "quantity": 2,
            "price": 25.98
        }
        
        item = OrderItemResponse(**data)
        assert item.id == 1
        assert item.dish_id == 5
        assert item.quantity == 2
        assert item.price == 25.98


class TestOrderCreateSchema:
    """Тесты для схемы OrderCreate"""
    
    def test_order_create_creation(self):
        """Тест создания OrderCreate"""
        data = {
            "user_id": 1,
            "items": [
                {"dish_id": 1, "quantity": 2},
                {"dish_id": 2, "quantity": 1}
            ]
        }
        
        order = OrderCreate(**data)
        assert order.user_id == 1
        assert len(order.items) == 2
        assert order.items[0].dish_id == 1
        assert order.items[0].quantity == 2
    
    def test_order_create_empty_items(self):
        """Тест создания OrderCreate с пустым списком items"""
        data = {
            "user_id": 1,
            "items": []
        }
        
        order = OrderCreate(**data)
        assert len(order.items) == 0


class TestOrderResponseSchema:
    """Тесты для схемы OrderResponse"""
    
    def test_order_response_creation(self):
        """Тест создания OrderResponse"""
        data = {
            "id": 123,
            "user_id": 1,
            "status": "pending",
            "total_price": 38.97,
            "created_at": "2024-01-01T12:00:00",
            "items": [
                {
                    "id": 1,
                    "dish_id": 5,
                    "quantity": 2,
                    "price": 25.98
                }
            ]
        }
        
        order = OrderResponse(**data)
        assert order.id == 123
        assert order.user_id == 1
        assert order.status == "pending"
        assert order.total_price == 38.97
        assert order.created_at == "2024-01-01T12:00:00"
        assert len(order.items) == 1
