from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Numeric,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from shared.database import Base

# === Таблица нутриентов (витамины + микроэлементы) ===
class Nutrient(Base):
    """
    Справочник всех нутриентов: витамины и минералы.
    Используется для связи с ингредиентами и суточными нормами.
    """
    __tablename__ = "nutrients"
    __table_args__ = {
        "comment": "Справочник витаминов и минералов (нутриентов), используемых в расчётах."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор нутриента.",
    )
    name = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Полное название нутриента (например, 'Витамин A (РЭ)', 'Кальций').",
    )
    short_name = Column(
        String,
        nullable=False,
        comment="Краткое обозначение нутриента (A, C, D, Ca, Fe и т.п.).",
    )
    type = Column(
        String,
        nullable=False,
        comment="Тип нутриента: 'vitamin' или 'mineral'.",
    )
    unit = Column(
        String,
        nullable=False,
        comment="Единица измерения нутриента (мг, мкг, мг и т.п.).",
    )

    code = Column(
        String,
        unique=True,
        nullable=False,
        comment="Стойкий код нутриента для API: 'vitamin_a', 'vitamin_c', 'calcium' и т.п.",
    )

    requirements = relationship(
        "DailyNutrientRequirement", back_populates="nutrient", cascade="all, delete-orphan"
    )
    contents = relationship(
        "IngredientNutrientContent", back_populates="nutrient", cascade="all, delete-orphan"
    )
    organ_benefits = relationship(
        "NutrientOrganBenefit", back_populates="nutrient", cascade="all, delete-orphan"
    )


# === Таблица органов ===
class Organ(Base):
    """
    Справочник органов/систем организма для описания пользы нутриентов.
    """
    __tablename__ = "organs"
    __table_args__ = {
        "comment": "Целевые органы и системы организма (печень, сердце, мозг и т.п.)."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор органа.",
    )
    name = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Название органа (например, 'Печень', 'Сердце').",
    )
    description = Column(
        String,
        comment="Краткое описание функции органа.",
    )

    benefits = relationship(
        "NutrientOrganBenefit", back_populates="organ", cascade="all, delete-orphan"
    )


# === Связь: нутриент -> орган (польза) ===
class NutrientOrganBenefit(Base):
    """
    Описывает, как конкретный нутриент влияет на конкретный орган.
    """
    __tablename__ = "nutrient_organ_benefits"
    __table_args__ = {
        "comment": "Текстовые описания пользы нутриентов для конкретных органов."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор записи пользы.",
    )
    nutrient_id = Column(
        Integer,
        ForeignKey("nutrients.id"),
        nullable=False,
        comment="FK на нутриент (витамин/минерал), оказывающий эффект.",
    )
    organ_id = Column(
        Integer,
        ForeignKey("organs.id"),
        nullable=False,
        comment="FK на орган, на который влияет нутриент.",
    )
    benefit_note = Column(
        String,
        nullable=False,
        comment="Краткое описание пользы нутриента для органа.",
    )

    nutrient = relationship("Nutrient", back_populates="organ_benefits")
    organ = relationship("Organ", back_populates="benefits")


# === Суточные нормы нутриентов ===
class DailyNutrientRequirement(Base):
    """
    Суточные рекомендуемые нормы потребления нутриентов для разных возрастных групп.
    """
    __tablename__ = "daily_nutrient_requirements"
    __table_args__ = {
        "comment": "Суточные рекомендуемые нормы нутриентов по возрастным группам."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор записи нормы.",
    )
    nutrient_id = Column(
        Integer,
        ForeignKey("nutrients.id"),
        nullable=False,
        comment="FK на нутриент, для которого задаётся норма.",
    )
    amount = Column(
        Float,
        nullable=False,
        comment="Рекомендуемое количество нутриента в сутки.",
    )
    age_group = Column(
        String,
        nullable=False,
        comment="Возрастная группа (например, 'взрослый').",
    )

    nutrient = relationship("Nutrient", back_populates="requirements")


# === Таблица блюд ===
class Dish(Base):
    __tablename__ = "dishes"
    __table_args__ = {"comment": "Блюда, доступные пользователю."}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
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
    ingredients = relationship("DishIngredient", back_populates="dish")


# === Таблица ингредиентов ===
class Ingredient(Base):
    __tablename__ = "ingredients"
    __table_args__ = {"comment": "Ингредиенты, используемые в блюдах."}

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="ID ингредиента."
    )
    name = Column(
        String,
        unique=True,
        index=True,
        nullable=False,
        comment="Название ингредиента."
    )
    category = Column(
        String,
        nullable=True,
        comment="Категория ингредиента (овощи, белки, орехи, масла и т.п.).",
    )

    dishes = relationship("DishIngredient", back_populates="ingredient")
    nutrient_contents = relationship("IngredientNutrientContent", back_populates="ingredient")


# === Связующая таблица: блюдо -> ингредиенты ===
class DishIngredient(Base):
    """
    Состав блюда: какие ингредиенты и в каком количестве (в граммах) используются.
    """
    __tablename__ = "dish_ingredients"
    __table_args__ = {
        "comment": "Связь блюд с ингредиентами и их массой в рецепте."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор записи состава блюда.",
    )
    dish_id = Column(
        Integer,
        ForeignKey("dishes.id"),
        nullable=False,
        comment="FK на блюдо.",
    )
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id"),
        nullable=False,
        comment="FK на ингредиент.",
    )
    amount_grams = Column(
        Float,
        nullable=False,
        comment="Масса ингредиента в блюде (граммы).",
    )

    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dishes")


# === Нутриенты в ингредиентах (витамины + минералы) ===
class IngredientNutrientContent(Base):
    """
    Содержание нутриентов (витаминов и минералов) в каждом ингредиенте на 100 г.
    Используется для расчёта профиля блюд.
    """
    __tablename__ = "ingredient_nutrient_contents"
    __table_args__ = {
        "comment": "Таблица содержания нутриентов в ингредиентах на 100 грамм."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор записи содержания нутриента.",
    )
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id"),
        nullable=False,
        comment="FK на ингредиент.",
    )
    nutrient_id = Column(
        Integer,
        ForeignKey("nutrients.id"),
        nullable=False,
        comment="FK на нутриент (витамин или минерал).",
    )
    content_per_100g = Column(
        Float,
        nullable=False,
        comment="Кол-во нутриента на 100 г ингредиента (в единицах из nutrients.unit).",
    )

    ingredient = relationship("Ingredient", back_populates="nutrient_contents")
    nutrient = relationship("Nutrient", back_populates="contents")


class IngredientCalories(Base):
    """
    Калорийность и макронутриенты ингредиента на 100 г.
    Используется для расчёта БЖУ блюд.
    """
    __tablename__ = "ingredient_calories"
    __table_args__ = {
        "comment": "Калории и макронутриенты ингредиентов на 100 г."
    }

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        comment="Уникальный идентификатор записи калорийности.",
    )
    ingredient_id = Column(
        Integer,
        ForeignKey("ingredients.id"),
        nullable=False,
        unique=True,
        comment="FK на ингредиент (одна запись калорийности на ингредиент).",
    )
    calories_per_100g = Column(
        Float,
        nullable=False,
        comment="Энергетическая ценность на 100 г ингредиента (ккал).",
    )
    protein_g = Column(
        Float,
        nullable=False,
        comment="Белки на 100 г (г).",
    )
    fat_g = Column(
        Float,
        nullable=False,
        comment="Жиры на 100 г (г).",
    )
    carbs_g = Column(
        Float,
        nullable=False,
        comment="Углеводы на 100 г (г).",
    )

    ingredient = relationship(
        "Ingredient",
        backref="calories",
        uselist=False,
    )


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
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    status = Column(String, default="offline")  # offline, available, going_to_pickup, picked_up, delivering
    current_order_id = Column(Integer, nullable=True)  # если везёт заказ

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

