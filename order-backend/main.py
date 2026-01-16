import json
import os

from confluent_kafka import Producer
from decimal import Decimal
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from shared.models import (
    FoodNutrient, Nutrient, NutrientRu,
    DailyNorm, Order, OrderItem
)

from shared.shared_models import (
    Dish, DishFood, Food
)

app = FastAPI(title="Order Service")
topic="new_orders"

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:80",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Kafka Producer ===
_producer: Producer | None = None


def _delivery_report(err, msg):
    if err is not None:
        # здесь можно заменить на нормальный логгер TODO
        print(f"Message delivery failed: {err}")
    # else:
    #     print(f"Message delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


def get_kafka_producer() -> Producer:
    global _producer
    if _producer is None:
        bootstrap = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        _producer = Producer(
            {
                "bootstrap.servers": bootstrap,
                # TODO
                # "enable.idempotence": True,
                # "linger.ms": 5,
                # "batch.num.messages": 10000,
            }
        )
    return _producer

# === Pydantic Models ===

class NutrientInfo(BaseModel):
    """Информация о нутриенте"""
    name: str
    unit_name: str
    amount: int  # округленное до целого значение
    daily_percentage: Optional[int] = None  # процент от суточной нормы

class DishNutrientsResponse(BaseModel):
    """Нутриенты блюда"""
    dish_id: int
    dish_name: str
    total_weight_g: float
    nutrients: Dict[str, NutrientInfo]  # ключ - nutrient_id

class OrderNutrientsResponse(BaseModel):
    """Нутриенты заказа"""
    order_id: int
    total_nutrients: Dict[str, NutrientInfo]
    dishes: List[DishNutrientsResponse]

class UserNutrientsResponse(BaseModel):
    """Нутриенты всех заказов пользователя"""
    user_id: int
    total_nutrients: Dict[str, NutrientInfo]
    order_count: int

class MenuMacros(BaseModel):
    """Макронутриенты для меню"""
    calories: int
    protein: int
    fat: int
    carbs: int

class MenuMicronutrient(BaseModel):
    """Микронутриент для меню"""
    name: str
    unit: str
    value: int
    coverage_percent: int

class MenuDish(BaseModel):
    """Блюдо в меню"""
    id: int
    name: str
    price: float
    description: Optional[str] = None
    macros: MenuMacros
    micronutrients: Dict[str, MenuMicronutrient]  # ключ - nutrient_id
    recommendations: List[str]
    score: Optional[int] = None
    image_url: Optional[str] = None

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

# === Функции для работы с нутриентами ===

def get_nutrients_with_translation(db: Session) -> Dict[int, Dict]:
    """Получить все нутриенты с русским переводом"""
    nutrients = db.query(Nutrient, NutrientRu).join(
        NutrientRu, Nutrient.id == NutrientRu.nutrient_id
    ).all()
    
    result = {}
    for nutrient, nutrient_ru in nutrients:
        result[nutrient.id] = {
            'name': nutrient_ru.name_ru,
            'name_en': nutrient.name,
            'unit_name': nutrient.unit_name
        }
    
    return result

def get_dish_nutrients(db: Session, dish_id: int) -> Dict[str, NutrientInfo]:
    """
    Получить все нутриенты для блюда с расчетом на 100г
    Используем только нутриенты из nutrient_ru
    """
    # Получаем нутриенты с русским переводом
    nutrients_map = get_nutrients_with_translation(db)
    
    # Получаем состав блюда
    dish_foods = db.query(DishFood).filter(DishFood.dish_id == dish_id).all()
    
    # Общий вес блюда
    total_weight = sum(df.amount_grams for df in dish_foods) or 1
    
    # Собираем нутриенты
    nutrient_totals = {}
    
    for dish_food in dish_foods:
        # Коэффициент для пересчета на 100г блюда
        factor = dish_food.amount_grams / total_weight
        
        # Получаем нутриенты для этого продукта
        food_nutrients = db.query(FoodNutrient).filter(
            FoodNutrient.fdc_id == dish_food.food_id,
            FoodNutrient.nutrient_id.in_(nutrients_map.keys())
        ).all()
        
        for food_nutrient in food_nutrients:
            nutrient_id = food_nutrient.nutrient_id
            if nutrient_id not in nutrient_totals:
                nutrient_totals[nutrient_id] = 0.0
            
            # Добавляем нутриент с учетом веса ингредиента
            nutrient_totals[nutrient_id] += float(food_nutrient.amount or 0) * factor
    
    # Преобразуем в NutrientInfo
    result = {}
    for nutrient_id, amount in nutrient_totals.items():
        if nutrient_id not in nutrients_map:
            continue
            
        nutrient_info = nutrients_map[nutrient_id]
        
        # Рассчитываем процент от суточной нормы
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == nutrient_id).first()
        daily_percentage = None
        
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = int(round((amount / float(daily_norm.amount)) * 100))
        
        # Округляем значение до целого
        rounded_amount = int(round(amount))
        
        result[str(nutrient_id)] = NutrientInfo(
            name=nutrient_info['name'],
            unit_name=nutrient_info['unit_name'].lower(),
            amount=rounded_amount,
            daily_percentage=daily_percentage
        )
    
    return result

def get_order_nutrients(db: Session, order_id: int) -> OrderNutrientsResponse:
    """
    Получить нутриенты для заказа
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    
    total_nutrients = {}
    dish_responses = []
    
    for item in order_items:
        # Получаем нутриенты для блюда
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            continue
            
        dish_nutrients = get_dish_nutrients(db, item.dish_id)
        
        # Умножаем на количество порций
        for key, nutrient in dish_nutrients.items():
            if key not in total_nutrients:
                total_nutrients[key] = NutrientInfo(
                    name=nutrient.name,
                    unit_name=nutrient.unit_name,
                    amount=0,
                    daily_percentage=0
                )
            
            # Обновляем значения
            total_nutrients[key].amount += nutrient.amount * item.quantity

        
        # Добавляем информацию о блюде
        dish_responses.append(DishNutrientsResponse(
            dish_id=dish.id,
            dish_name=dish.name,
            total_weight_g=100.0,
            nutrients=dish_nutrients
        ))
    
    # Рассчитываем проценты для общих нутриентов
    nutrients_map = get_nutrients_with_translation(db)
    
    for key, nutrient in total_nutrients.items():
        nutrient_id = int(key)
        
        # Рассчитываем процент от суточной нормы
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == nutrient_id).first()
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = int(round((nutrient.amount / float(daily_norm.amount)) * 100))
            nutrient.daily_percentage = daily_percentage
    
    return OrderNutrientsResponse(
        order_id=order_id,
        total_nutrients=total_nutrients,
        dishes=dish_responses
    )

def get_user_total_nutrients(db: Session, user_id: int) -> UserNutrientsResponse:
    """
    Получить общие нутриенты из всех заказов пользователя
    """
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    
    total_nutrients = {}
    
    for order in orders:
        try:
            order_nutrients = get_order_nutrients(db, order.id)
            
            # Суммируем нутриенты из этого заказа
            for key, nutrient in order_nutrients.total_nutrients.items():
                if key not in total_nutrients:
                    total_nutrients[key] = NutrientInfo(
                        name=nutrient.name,
                        unit_name=nutrient.unit_name,
                        amount=0,
                        daily_percentage=0
                    )
                total_nutrients[key].amount += nutrient.amount
        except HTTPException:
            continue
    
    # Рассчитываем проценты для общих нутриентов
    for key, nutrient in total_nutrients.items():
        nutrient_id = int(key)
        
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == nutrient_id).first()
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = int(round((nutrient.amount / float(daily_norm.amount)) * 100))
            nutrient.daily_percentage = daily_percentage
    
    return UserNutrientsResponse(
        user_id=user_id,
        total_nutrients=total_nutrients,
        order_count=len(orders)
    )

# === API Endpoints ===

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/dishes/{dish_id}/nutrients", response_model=DishNutrientsResponse)
def get_dish_nutrients_endpoint(dish_id: int, db: Session = Depends(get_db)):
    """
    Получить нутриенты для конкретного блюда
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    nutrients = get_dish_nutrients(db, dish_id)
    
    # Рассчитываем общий вес блюда
    dish_foods = db.query(DishFood).filter(DishFood.dish_id == dish_id).all()
    total_weight = sum(df.amount_grams for df in dish_foods)
    
    return DishNutrientsResponse(
        dish_id=dish.id,
        dish_name=dish.name,
        total_weight_g=total_weight,
        nutrients=nutrients
    )

@app.get("/orders/{order_id}/nutrients", response_model=OrderNutrientsResponse)
def get_order_nutrients_endpoint(order_id: int, db: Session = Depends(get_db)):
    """
    Получить нутриенты для конкретного заказа
    """
    return get_order_nutrients(db, order_id)

@app.get("/users/{user_id}/nutrients", response_model=UserNutrientsResponse)
def get_user_nutrients_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Получить общие нутриенты из всех заказов пользователя
    """
    return get_user_total_nutrients(db, user_id)

@app.get("/menu/", response_model=List[MenuDish])
def get_menu(db: Session = Depends(get_db)):
    """Получить меню с нутриентами"""
    dishes = db.query(Dish).all()
    
    menu: List[MenuDish] = []
    
    for dish in dishes:
        # Получаем нутриенты блюда
        dish_nutrients = get_dish_nutrients(db, dish.id)
        
        # Извлекаем макронутриенты
        protein = dish_nutrients.get('1003', NutrientInfo(name='', unit_name='', amount=0)).amount
        fat = dish_nutrients.get('1004', NutrientInfo(name='', unit_name='', amount=0)).amount
        carbs = dish_nutrients.get('1005', NutrientInfo(name='', unit_name='', amount=0)).amount
        
        # Рассчитываем калории: 4*белки + 9*жиры + 4*углеводы
        calories = protein * 4 + fat * 9 + carbs * 4
        
        # Макронутриенты
        macros = MenuMacros(
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs
        )
        
        # Собираем микронутриенты (все кроме макро)
        micronutrients = {}
        for nutrient_id_str, nutrient in dish_nutrients.items():
            if nutrient_id_str not in ['1003', '1004', '1005']:
                micronutrients[nutrient_id_str] = MenuMicronutrient(
                    name=nutrient.name,
                    unit=nutrient.unit_name,
                    value=nutrient.amount,
                    coverage_percent=nutrient.daily_percentage or 0
                )
        
        # Генерируем рекомендации
        recommendations = []
        
        if protein > 15:
            recommendations.append("Богато белком")
        if fat < 5:
            recommendations.append("Низкое содержание жиров")
        if carbs > 30:
            recommendations.append("Хороший источник энергии")
        
        # Рекомендации по микронутриентам
        for nutrient_id_str, nutrient in dish_nutrients.items():
            if nutrient.daily_percentage and nutrient.daily_percentage > 20:
                recommendations.append(f"Содержит {nutrient.name}")
        
        # Убираем дубликаты и ограничиваем количество
        recommendations = list(dict.fromkeys(recommendations))[:3]
        
        # Вычисляем оценку
        score = 5
        
        if protein > 15:
            score += 1
        if fat < 10:
            score += 1
        
        nutrient_count = len(micronutrients)
        if nutrient_count > 5:
            score += 1
        if nutrient_count > 10:
            score += 1
        
        score = min(10, max(1, score))
        
        menu.append(
            MenuDish(
                id=dish.id,
                name=dish.name,
                price=float(dish.price),
                description=dish.description,
                macros=macros,
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
    total = Decimal('0.00')
    order_items = []
    
    for item in order_data.items:
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            raise HTTPException(status_code=404, detail=f"Dish {item.dish_id} not found")
        
        item_total = dish.price * item.quantity
        total += item_total
        
        order_items.append({
            "dish_id": item.dish_id,
            "quantity": item.quantity,
            "price": dish.price
        })
    
    # Создаём заказ
    order = Order(
        user_id=order_data.user_id,
        total_price=total,
        status="pending"
    )
    db.add(order)
    db.flush()
    
    # Создаём OrderItem
    for item in order_items:
        order_item = OrderItem(
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
    payload = {
        "order_id": order.id,
        "user_id": order.user_id,
        "total_price": float(total),
        "status": "pending",
    }

    producer.produce(
        topic=topic,
        value=json.dumps(payload).encode("utf-8"),
        callback=_delivery_report,
    )
    # обработать callbacks (delivery_report)
    producer.poll(0)
    producer.flush()
    
    # Возвращаем заказ
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_price=float(order.total_price),
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
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    result = []
    
    for order in orders:
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        result.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                status=order.status,
                total_price=float(order.total_price),
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

@app.get("/dishes/", response_model=List[DishResponse])
def get_all_dishes(db: Session = Depends(get_db)):
    """Получить список всех блюд (упрощенный формат)"""
    dishes = db.query(Dish).all()
    return [
        DishResponse(id=dish.id, name=dish.name, price=float(dish.price))
        for dish in dishes
    ]
