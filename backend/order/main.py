from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import threading
from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from shared.database import SessionLocal
from shared.models import (
    Dish as DishModel,
    DishIngredient as DishIngredientModel,
    Ingredient as IngredientModel,
    Nutrient as NutrientModel,
    DailyNutrientRequirement as DailyNutrientRequirementModel,
    IngredientNutrientContent as IngredientNutrientContentModel,
    IngredientCalories as IngredientCaloriesModel,
)


import os

app = FastAPI(title="Order Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # Vite dev server (если используется)
        "http://localhost:3000",           # Основной порт (если настроен nginx)
        "http://localhost:3001",           # Admin frontend
        "http://localhost:3002",           # Order frontend  
        "http://localhost:3003",           # Courier frontend
        "http://localhost:80",             # Nginx proxy (если используется)
        "http://localhost",                # Nginx без порта
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Kafka Producer ===
producer = None

def get_kafka_producer():
    global producer
    if not producer:
        producer = KafkaProducer(
            bootstrap_servers=[os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return producer

# === Pydantic Models ===

class MenuMicronutrient(BaseModel):
    name: str
    unit: str
    value: float
    coverage_percent: float


class MenuMacros(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float


class MenuDish(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    macros: MenuMacros
    micronutrients: Dict[str, MenuMicronutrient]
    recommendations: List[str]
    score: Optional[int] = None
    image_url: Optional[str] = None  # может быть Null или строкой

class DishResponse(BaseModel):
    id: int
    name: str
    price: float


class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: str
    items: List[OrderItemResponse]

# === API Endpoints ===

@app.get("/menu/", response_model=List[MenuDish])
def get_menu(db: Session = Depends(get_db)):
    dishes = db.query(DishModel).all()

    daily_req_rows = (
        db.query(DailyNutrientRequirementModel)
        .filter(DailyNutrientRequirementModel.age_group == "взрослый")
        .all()
    )
    daily_req = {r.nutrient_id: r for r in daily_req_rows}

    menu: List[MenuDish] = []

    for dish in dishes:
        di_rows = (
            db.query(DishIngredientModel)
            .filter(DishIngredientModel.dish_id == dish.id)
            .all()
        )

        total_calories = 0.0
        total_protein = 0.0
        total_fat = 0.0
        total_carbs = 0.0
        nutrient_totals: Dict[int, float] = {}

        for di in di_rows:
            ingredient = db.query(IngredientModel).filter(
                IngredientModel.id == di.ingredient_id
            ).first()
            if not ingredient:
                continue

            cal = db.query(IngredientCaloriesModel).filter(
                IngredientCaloriesModel.ingredient_id == ingredient.id
            ).first()

            factor = di.amount_grams / 100.0

            if cal:
                total_calories += (cal.calories_per_100g or 0) * factor
                total_protein += (cal.protein_g or 0) * factor
                total_fat += (cal.fat_g or 0) * factor
                total_carbs += (cal.carbs_g or 0) * factor

            inc_rows = (
                db.query(IngredientNutrientContentModel)
                .filter(IngredientNutrientContentModel.ingredient_id == ingredient.id)
                .all()
            )
            for inc in inc_rows:
                nutrient_totals.setdefault(inc.nutrient_id, 0.0)
                nutrient_totals[inc.nutrient_id] += (inc.content_per_100g or 0) * factor


        # Сформируем словарь микронутриентов в стиле nutrition_api_data.json
        micronutrients: Dict[str, MenuMicronutrient] = {}
        recommendations: List[str] = []
        score = None
        for nutrient_id, value in nutrient_totals.items():
            nutrient = db.query(NutrientModel).filter(
                NutrientModel.id == nutrient_id
            ).first()
            if not nutrient:
                continue

            dr = daily_req.get(nutrient_id)
            coverage = 0.0
            if dr and dr.amount and dr.amount > 0:
                coverage = (value / dr.amount) * 100.0

            # Используем стойкий код из таблицы nutrients
            key = nutrient.code  # например 'vitamin_a', 'selenium', 'calcium'

            micronutrients[key] = MenuMicronutrient(
                name=nutrient.name,
                unit=nutrient.unit,
                value=round(value, 1),
                coverage_percent=round(coverage, 1),
            )

        
        # Простая эвристика для рекомендаций/score
        if total_protein > 60:
            recommendations.append("Высокобелковое блюдо")
        if "vitamin_c" in micronutrients and micronutrients["vitamin_c"].coverage_percent >= 100:
            recommendations.append("Поддержка иммунитета (высокий витамин C)")
        if "selenium" in micronutrients and micronutrients["selenium"].coverage_percent >= 150:
            recommendations.append("Поддержка щитовидной железы (селен)")

        # score как суммарная оценка (очень грубо)
        score = min(
            10,
            int(
                (total_protein / 10)
                + (micronutrients.get("vitamin_c", MenuMicronutrient(name="", unit="", value=0, coverage_percent=0)).coverage_percent / 100)
            ),
        )

        menu.append(
            MenuDish(
                id=dish.id,
                name=dish.name,
                price=float(dish.price),
                description=getattr(dish, "description", None),
                macros=MenuMacros(
                    calories=round(total_calories, 1),
                    protein=round(total_protein, 1),
                    fat=round(total_fat, 1),
                    carbs=round(total_carbs, 1),
                ),
                micronutrients=micronutrients,
                recommendations=recommendations,
                score=score,
                image_url=dish.image_url,
            )
        )

    return menu


@app.post("/orders/", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    # Считаем общую сумму
    total = 0
    order_items = []

    for item in order_data.items:
        dish = db.query(DishModel).filter(DishModel.id == item.dish_id).first()
        if not dish:
            raise HTTPException(status_code=404, detail=f"Dish {item.dish_id} not found")
        total += dish.price * item.quantity
        order_items.append({
            "dish_id": item.dish_id,
            "quantity": item.quantity,
            "price": dish.price,
            "image_url": dish.image_url
        })

    # Создаём заказ
    order = OrderModel(user_id=order_data.user_id, total_price=total, status="pending")
    db.add(order)
    db.flush()

    # Создаём OrderItem
    for item in order_items:
        order_item = OrderItemModel(
            order_id=order.id,
            dish_id=item["dish_id"],
            quantity=item["quantity"],
            price=item["price"]
        )
        db.add(order_item)

    db.commit()
    db.refresh(order)

    # Отправляем в Kafka
    producer = get_kafka_producer()
    producer.send('new_orders', {'order_id': order.id, 'user_id': order.user_id})
    producer.flush()

    # Возвращаем заказ
    items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_price=order.total_price,
        created_at=order.created_at.isoformat(),
        items=[
            OrderItemResponse(
                id=it.id,
                dish_id=it.dish_id,
                quantity=it.quantity,
                price=float(it.price)
            )
            for it in items
        ]
    )

@app.get("/orders/{user_id}", response_model=List[OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    orders = db.query(OrderModel).filter(OrderModel.user_id == user_id).all()
    result = []

    for order in orders:
        items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
        result.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                total_price=order.total_price,
                created_at=order.created_at.isoformat(),
                items=[
                    OrderItemResponse(
                        id=it.id,
                        dish_id=it.dish_id,
                        quantity=it.quantity,
                        price=float(it.price)
                    )
                    for it in items
                ]
            )
        )

    return result

@app.get("/health")
def health_check():
    return {"status": "ok"}


