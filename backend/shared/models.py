from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from shared.database import Base

# === Таблицы для Food Service ===
# 
class Vitamin(Base):
    __tablename__ = "vitamins"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    short_name = Column(String)

    benefits = relationship("VitaminOrganBenefit", back_populates="vitamin")
    requirements = relationship("DailyVitaminRequirement", back_populates="vitamin")
    contents = relationship("IngredientVitaminContent", back_populates="vitamin")

class Organ(Base):
    __tablename__ = "organs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)

    benefits = relationship("VitaminOrganBenefit", back_populates="organ")

class VitaminOrganBenefit(Base):
    __tablename__ = "vitamin_organ_benefits"
    id = Column(Integer, primary_key=True, index=True)
    vitamin_id = Column(Integer, ForeignKey("vitamins.id"))
    organ_id = Column(Integer, ForeignKey("organs.id"))
    benefit_note = Column(String)

    vitamin = relationship("Vitamin", back_populates="benefits")
    organ = relationship("Organ", back_populates="benefits")

class DailyVitaminRequirement(Base):
    __tablename__ = "daily_vitamin_requirements"
    id = Column(Integer, primary_key=True, index=True)
    vitamin_id = Column(Integer, ForeignKey("vitamins.id"))
    amount = Column(Float)
    unit = Column(String)
    age_group = Column(String)

    vitamin = relationship("Vitamin", back_populates="requirements")

class Dish(Base):
    __tablename__ = "dishes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    price = Column(Numeric)

    ingredients = relationship("DishIngredient", back_populates="dish")

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    dishes = relationship("DishIngredient", back_populates="ingredient")
    vitamin_contents = relationship("IngredientVitaminContent", back_populates="ingredient")

class DishIngredient(Base):
    __tablename__ = "dish_ingredients"
    id = Column(Integer, primary_key=True, index=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    amount_grams = Column(Float)

    dish = relationship("Dish", back_populates="ingredients")
    ingredient = relationship("Ingredient", back_populates="dishes")

class IngredientVitaminContent(Base):
    __tablename__ = "ingredient_vitamin_contents"
    id = Column(Integer, primary_key=True, index=True)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id"))
    vitamin_id = Column(Integer, ForeignKey("vitamins.id"))
    content_per_100g = Column(Float)
    unit = Column(String)

    ingredient = relationship("Ingredient", back_populates="vitamin_contents")
    vitamin = relationship("Vitamin", back_populates="contents")


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

