from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base

class Food(Base):
    """
    Основная таблица продуктов USDA FDC.
    Содержит описание и метаданные продуктов.
    Дедупликация: храним только уникальные по description + food_category_id.
    """
    __tablename__ = "food"
    
    fdc_id = Column(Integer, primary_key=True, comment="Уникальный ID продукта в FDC")
    description = Column(String(500), nullable=True, index=True, comment="Название продукта (может содержать коды сэмплов)")
    food_category_id = Column(String(16), comment="ID категории продукта (Branded, Foundation и т.д.)")
    
    # Связи 1:M
    nutrients = relationship("FoodNutrient", back_populates="food", cascade="all, delete-orphan")
    ru_names = relationship("FoodRu", back_populates="food")
    
    # Индексы для дедупликации и поиска
    __table_args__ = (
        Index('idx_food_category_date', 'food_category_id'),
        Index('idx_food_normalized_desc', 'description', postgresql_ops={'description': 'varchar_pattern_ops'}),
    )


class Nutrient(Base):
    """
    Справочник нутриентов. Фильтруем только ~25 популярных (БЖУ, витамины, минералы).
    """
    __tablename__ = "nutrient"
    
    id = Column(Integer, primary_key=True, comment="Уникальный ID нутриента в FDC")
    name = Column(String(255), nullable=False, comment="Название нутриента на английском")
    unit_name = Column(String(50), comment="Единица измерения (g, mg, mcg, IU)")
    nutrient_nbr = Column(Float, comment="Старый номер нутриента из SR Legacy (для совместимости)")
    
    # Связи 1:M
    food_nutrients = relationship("FoodNutrient", back_populates="nutrient")
    ru_names = relationship("NutrientRu", back_populates="nutrient")


class FoodNutrient(Base):
    """
    Связующая таблица: продукт-нутриент. amount = количество на 100г.
    """
    __tablename__ = "food_nutrient"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id", ondelete="CASCADE"), 
                    nullable=False, index=True, comment="Ссылка на продукт")
    nutrient_id = Column(Integer, ForeignKey("nutrient.id", ondelete="CASCADE"), 
                         nullable=False, index=True, comment="Ссылка на нутриент")
    amount = Column(Numeric(10, 4), nullable=True, comment="Количество на 100г продукта")
    data_points = Column(Integer, comment="Количество источников данных (надежность)")
    
    # Связи M:1
    food = relationship("Food", back_populates="nutrients")
    nutrient = relationship("Nutrient", back_populates="food_nutrients")
    
    __table_args__ = (
        Index('idx_food_nutr_composite', 'fdc_id', 'nutrient_id', unique=True),
    )


class FoodRu(Base):
    """Русская локализация названий продуктов"""
    __tablename__ = "food_ru"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fdc_id = Column(Integer, ForeignKey("food.fdc_id"), nullable=False, index=True)
    name_ru = Column(String(255), nullable=False, comment="Короткое название на русском")
    description_ru = Column(Text, comment="Полное описание на русском")
    
    food = relationship("Food")


class NutrientRu(Base):
    """Русская локализация нутриентов"""
    __tablename__ = "nutrient_ru"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    nutrient_id = Column(Integer, ForeignKey("nutrient.id"), nullable=False, unique=True, index=True)
    name_ru = Column(String(255), nullable=False)
    unit_ru = Column(String(50))
    
    nutrient = relationship("Nutrient")


# === Суточные нормы нутриентов ===
class DailyNorm(Base):
    """
    Рекомендуемые суточные нормы потребления для взрослого (средние значения).
    Источник: Роспотребнадзор MP 2.3.1.0253-21 + WHO. 
    Для мужчин 30-50 лет, умеренная активность (~2500 ккал).
    """
    __tablename__ = "daily_norms"
    
    nutrient_id = Column(Integer, ForeignKey("nutrient.id"), primary_key=True, comment="Ссылка на nutrient")
    amount = Column(Numeric(10, 4), nullable=False, comment="Норма на 100% суточной потребности")
    min_age = Column(Integer, default=18, comment="Минимальный возраст")
    max_age = Column(Integer, default=60, comment="Максимальный возраст")
    gender = Column(String(10), default="both", comment="Мужчины/Женщины/both")
    unit_name = Column(String(50), comment="Единица измерения")
    
    nutrient = relationship("Nutrient")
    
    __table_args__ = (Index('idx_daily_norm_nutrient', 'nutrient_id'),)

#----------------------------------------------------------------------
# === Таблица органов ===
# class Organ(Base):
#     """
#     Справочник органов/систем организма для описания пользы нутриентов.
#     """
#     __tablename__ = "organs"
#     __table_args__ = {
#         "comment": "Целевые органы и системы организма (печень, сердце, мозг и т.п.)."
#     }

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True,
#         comment="Уникальный идентификатор органа.",
#     )
#     name = Column(
#         String,
#         unique=True,
#         index=True,
#         nullable=False,
#         comment="Название органа (например, 'Печень', 'Сердце').",
#     )
#     description = Column(
#         String,
#         comment="Краткое описание функции органа.",
#     )

#     benefits = relationship(
#         "NutrientOrganBenefit", back_populates="organ", cascade="all, delete-orphan"
#     )


# === Связь: нутриент -> орган (польза) ===
# class NutrientOrganBenefit(Base):
#     """
#     Описывает, как конкретный нутриент влияет на конкретный орган.
#     """
#     __tablename__ = "nutrient_organ_benefits"
#     __table_args__ = {
#         "comment": "Текстовые описания пользы нутриентов для конкретных органов."
#     }

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True,
#         comment="Уникальный идентификатор записи пользы.",
#     )
#     nutrient_id = Column(
#         Integer,
#         ForeignKey("nutrients.id"),
#         nullable=False,
#         comment="FK на нутриент (витамин/минерал), оказывающий эффект.",
#     )
#     organ_id = Column(
#         Integer,
#         ForeignKey("organs.id"),
#         nullable=False,
#         comment="FK на орган, на который влияет нутриент.",
#     )
#     benefit_note = Column(
#         String,
#         nullable=False,
#         comment="Краткое описание пользы нутриента для органа.",
#     )

#     nutrient = relationship("Nutrient", back_populates="organ_benefits")
#     organ = relationship("Organ", back_populates="benefits")




# === Таблица блюд ===
class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = {"comment": "Блюда, доступные пользователю."}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="ID блюда."
    )
    name = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Название блюда."
    )
    price = Column(
        Numeric,
        nullable=False,
        comment="Цена блюда."
    )
    description = Column(
        String,
        nullable=True,
        comment="Краткое описание блюда (ингредиенты, способ приготовления).",
    )
    image_url = Column(
       String,
       nullable=True
    )
    ingredients = relationship("DishIngredient", back_populates="dish")


# === Связующая таблица: блюдо -> ингредиенты ===
# class DishIngredient(Base):
#     """
#     Состав блюда: какие ингредиенты и в каком количестве (в граммах) используются.
#     """
#     __tablename__ = "dish_ingredients"
#     __table_args__ = {
#         "comment": "Связь блюд с ингредиентами и их массой в рецепте."
#     }

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True,
#         comment="Уникальный идентификатор записи состава блюда.",
#     )
#     dish_id = Column(
#         Integer,
#         ForeignKey("dishes.id"),
#         nullable=False,
#         comment="FK на блюдо.",
#     )
#     ingredient_id = Column(
#         Integer,
#         ForeignKey("ingredients.id"),
#         nullable=False,
#         comment="FK на ингредиент.",
#     )
#     amount_grams = Column(
#         Float,
#         nullable=False,
#         comment="Масса ингредиента в блюде (граммы).",
#     )

#     dish = relationship("Dish", back_populates="ingredients")
#     ingredient = relationship("Ingredient", back_populates="dishes")


# === Нутриенты в ингредиентах (витамины + минералы) ===
# class IngredientNutrientContent(Base):
#     """
#     Содержание нутриентов (витаминов и минералов) в каждом ингредиенте на 100 г.
#     Используется для расчёта профиля блюд.
#     """
#     __tablename__ = "ingredient_nutrient_contents"
#     __table_args__ = {
#         "comment": "Таблица содержания нутриентов в ингредиентах на 100 грамм."
#     }

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True,
#         comment="Уникальный идентификатор записи содержания нутриента.",
#     )
#     ingredient_id = Column(
#         Integer,
#         ForeignKey("ingredients.id"),
#         nullable=False,
#         comment="FK на ингредиент.",
#     )
#     nutrient_id = Column(
#         Integer,
#         ForeignKey("nutrients.id"),
#         nullable=False,
#         comment="FK на нутриент (витамин или минерал).",
#     )
#     content_per_100g = Column(
#         Float,
#         nullable=False,
#         comment="Кол-во нутриента на 100 г ингредиента (в единицах из nutrients.unit).",
#     )

#     ingredient = relationship("Ingredient", back_populates="nutrient_contents")
#     nutrient = relationship("Nutrient", back_populates="contents")


# class IngredientCalories(Base):
#     """
#     Калорийность и макронутриенты ингредиента на 100 г.
#     Используется для расчёта БЖУ блюд.
#     """
#     __tablename__ = "ingredient_calories"
#     __table_args__ = {
#         "comment": "Калории и макронутриенты ингредиентов на 100 г."
#     }

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True,
#         comment="Уникальный идентификатор записи калорийности.",
#     )
#     ingredient_id = Column(
#         Integer,
#         ForeignKey("ingredients.id"),
#         nullable=False,
#         unique=True,
#         comment="FK на ингредиент (одна запись калорийности на ингредиент).",
#     )
#     calories_per_100g = Column(
#         Float,
#         nullable=False,
#         comment="Энергетическая ценность на 100 г ингредиента (ккал).",
#     )
#     protein_g = Column(
#         Float,
#         nullable=False,
#         comment="Белки на 100 г (г).",
#     )
#     fat_g = Column(
#         Float,
#         nullable=False,
#         comment="Жиры на 100 г (г).",
#     )
#     carbs_g = Column(
#         Float,
#         nullable=False,
#         comment="Углеводы на 100 г (г).",
#     )

#     ingredient = relationship(
#         "Ingredient",
#         backref="calories",
#         uselist=False,
#     )


# === Таблицы для Order Service ===
# 
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
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    quantity = Column(Integer, default=1)
    price = Column(Numeric(precision=10, scale=2))  # цена блюда на момент заказа

    order = relationship("Order", back_populates="items")
    dish = relationship("Dish")  # чтобы получить имя/цену блюда

# === Таблицы для Courier Service ===
# 
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

