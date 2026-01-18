from sqlalchemy import (
    Column, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, 
    Numeric, String, Text, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from shared.database import Base


class Dish(Base):
    """Блюда"""
    __tablename__ = "dish"
    __table_args__ = {"comment": "Блюда, доступные пользователю."}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Numeric, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    
    ingredients = relationship(
        "DishFood", 
        back_populates="dish",
        cascade="all, delete-orphan"
    )


class DishFood(Base):
    """Состав блюда"""
    __tablename__ = "dish_food"
    __table_args__ = {"comment": "Связь блюд с ингредиентами"}

    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dish.id", ondelete="CASCADE"), 
                    nullable=False, index=True)
    food_id = Column(Integer, ForeignKey("food.fdc_id", ondelete="CASCADE"), 
                    nullable=False, index=True)
    amount_grams = Column(Float, nullable=False)
    
    dish = relationship("Dish", back_populates="ingredients")
    food = relationship("Food", back_populates="dish")

class FoodRu(Base):
    """Русская локализация продуктов"""
    __tablename__ = "food_ru"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id", ondelete="CASCADE"), 
                   nullable=False, unique=True, index=True)
    name_ru = Column(String(255), nullable=False)
    food_category_id = Column(Integer, ForeignKey("food_category.id"))
    
    food = relationship("Food", back_populates="ru_names")

class Food(Base):
    """Основная таблица продуктов (упрощенная версия)"""
    __tablename__ = "food"
    __table_args__ = {"comment": "Продукты."}
    
    fdc_id = Column(Integer, primary_key=True, comment="Уникальный ID продукта FDC")
    description = Column(String(500), comment="Название на английском (description)")
    food_category_id = Column(Integer, ForeignKey("food_category.id"), 
                             comment="Ссылка на категорию")
    
    nutrients = relationship("FoodNutrient", back_populates="food")
    ru_names = relationship("FoodRu", back_populates="food", uselist=False)
    category = relationship("FoodCategory", back_populates="foods")
    dish = relationship("DishFood", back_populates="food")


class FoodCategory(Base):
    """Категории продуктов"""
    __tablename__ = "food_category"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True)
    description = Column(String(255), nullable=False)
    
    foods = relationship("Food", back_populates="category")
    ru_names = relationship("FoodCategoryRu", back_populates="category")
    
    __table_args__ = (Index('idx_food_category_code', 'code'),)

    
class FoodCategoryRu(Base):
    """Локализация категорий"""
    __tablename__ = "food_category_ru"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, ForeignKey("food_category.id"), 
                        nullable=False, unique=True, index=True)
    name_ru = Column(String(255), nullable=False)
    description_ru = Column(Text)
    
    category = relationship("FoodCategory", back_populates="ru_names")
