from sqlalchemy import (
    Column, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, 
    Numeric, String, Text, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from shared.database import Base

# === Food и связанные ===
class Food(Base):
    """Основная таблица продуктов (упрощенная версия)"""
    __tablename__ = "food"
    
    fdc_id = Column(Integer, primary_key=True, comment="Уникальный ID продукта FDC")
    description = Column(String(500), comment="Название на английском (description)")
    food_category_id = Column(Integer, ForeignKey("food_category.id"), 
                             comment="Ссылка на категорию")
    
    nutrients = relationship("FoodNutrient", back_populates="food")
    ru_names = relationship("FoodRu", back_populates="food", uselist=False)
    category = relationship("FoodCategory", back_populates="foods")
    dish = relationship("DishFood", back_populates="food")


class Nutrient(Base):
    """Справочник нутриентов"""
    __tablename__ = "nutrient"
    
    id = Column(Integer, primary_key=True, comment="Уникальный ID нутриента в FDC")
    name = Column(String(255), nullable=False, comment="Название на английском")
    unit_name = Column(String(50), comment="Единица измерения (g, mg, mcg, IU)")
    nutrient_nbr = Column(Float, comment="Старый номер нутриента из SR Legacy")
    
    food_nutrients = relationship("FoodNutrient", back_populates="nutrient")
    ru_names = relationship("NutrientRu", back_populates="nutrient")


class FoodNutrient(Base):
    """Продукт-нутриент"""
    __tablename__ = "food_nutrient"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id", ondelete="CASCADE"), 
                    nullable=False, index=True)
    nutrient_id = Column(Integer, ForeignKey("nutrient.id", ondelete="CASCADE"), 
                         nullable=False, index=True)
    amount = Column(Numeric(10, 4), nullable=True)
    data_points = Column(Integer)
    
    food = relationship("Food", back_populates="nutrients")
    nutrient = relationship("Nutrient", back_populates="food_nutrients")
    
    __table_args__ = (
        Index('idx_food_nutr_composite', 'fdc_id', 'nutrient_id', unique=True),
    )


class FoodRu(Base):
    """Русская локализация продуктов"""
    __tablename__ = "food_ru"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id", ondelete="CASCADE"), 
                   nullable=False, unique=True, index=True)
    name_ru = Column(String(255), nullable=False)
    food_category_id = Column(Integer, ForeignKey("food_category.id"))
    
    food = relationship("Food", back_populates="ru_names")


class NutrientRu(Base):
    """Русская локализация нутриентов"""
    __tablename__ = "nutrient_ru"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nutrient_id = Column(Integer, ForeignKey("nutrient.id"), 
                        nullable=False, unique=True, index=True)
    name_ru = Column(String(255), nullable=False)
    
    nutrient = relationship("Nutrient", back_populates="ru_names")


class DailyNorm(Base):
    """Суточные нормы"""
    __tablename__ = "daily_norms"
    
    nutrient_id = Column(Integer, ForeignKey("nutrient.id"), primary_key=True)
    amount = Column(Numeric(12, 4), nullable=False)
    unit_name = Column(String(50))
    source = Column(String(50), default="MP_2.3.1.0253-21")
    
    nutrient = relationship("Nutrient")


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


# === БЛЮДА===
class Dish(Base):
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


# ------------------------------------------------------------------------

# === Таблицы для Order Service ===
class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    status = Column(String, default="pending")
    total_price = Column(Numeric(precision=10, scale=2))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.current_timestamp())

    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    dish_id = Column(Integer, ForeignKey("dish.id"))
    quantity = Column(Integer, default=1)
    price = Column(Numeric(precision=10, scale=2))  # цена блюда на момент заказа

    order = relationship("Order", back_populates="items")
    dish = relationship("Dish")  # чтобы получить имя/цену блюда


# === Таблицы для Courier Service ===
class Courier(Base):
    __tablename__ = "couriers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String, default="offline")  # online, available, delivering, offline
    current_order_id = Column(Integer, nullable=True)
    photo_url = Column(String, nullable=True)  # ← Добавить


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    status = Column(String, default="assigned")  # assigned, picked_up, on_way, delivered
    assigned_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    picked_up_at = Column(TIMESTAMP(timezone=True), nullable=True)
    delivered_at = Column(TIMESTAMP(timezone=True), nullable=True)

    order = relationship("Order")
    courier = relationship("Courier")

# === Таблицы для Auth Service ===

