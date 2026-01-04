from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import os
from decimal import Decimal

from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from shared.models import (
    Dish, DishFood, Food, FoodNutrient, Nutrient, 
    DailyNorm, Order, OrderItem
)

app = FastAPI(title="Order Service")

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

class NutrientInfo(BaseModel):
    """Информация о нутриенте"""
    name: str
    unit_name: str
    amount: float
    daily_percentage: Optional[float] = None  # процент от суточной нормы

class DishNutrientsResponse(BaseModel):
    """Нутриенты блюда"""
    dish_id: int
    dish_name: str
    total_weight_g: float
    nutrients: Dict[str, NutrientInfo]  # ключ - nutrient_id или name

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
    calories: float
    protein: float
    fat: float
    carbs: float

class MenuMicronutrient(BaseModel):
    name: str
    unit: str
    value: float
    coverage_percent: float

class MenuDish(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    macros: MenuMacros
    micronutrients: Dict[str, MenuMicronutrient]
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

# === Вспомогательные функции ===

def get_dish_nutrients(db: Session, dish_id: int) -> Dict[str, NutrientInfo]:
    """
    Получить все нутриенты для блюда с расчетом на 100г
    """
    # Получаем состав блюда
    dish_foods = db.query(DishFood).filter(DishFood.dish_id == dish_id).all()
    
    # Общий вес блюда
    total_weight = sum(df.amount_grams for df in dish_foods)
    
    # Собираем нутриенты
    nutrients = {}
    
    for dish_food in dish_foods:
        # Коэффициент для пересчета на 100г блюда
        factor = dish_food.amount_grams / total_weight
        
        # Получаем нутриенты для этого продукта
        food_nutrients = db.query(FoodNutrient, Nutrient).join(
            Nutrient, Nutrient.id == FoodNutrient.nutrient_id
        ).filter(FoodNutrient.fdc_id == dish_food.food_id).all()
        
        for food_nutrient, nutrient in food_nutrients:
            key = str(nutrient.id)
            if key not in nutrients:
                nutrients[key] = {
                    'name': nutrient.name,
                    'unit_name': nutrient.unit_name,
                    'amount': 0.0
                }
            
            # Добавляем нутриент с учетом веса ингредиента
            nutrients[key]['amount'] += float(food_nutrient.amount or 0) * factor
    
    # Преобразуем в NutrientInfo
    result = {}
    for key, nutrient_data in nutrients.items():
        # Рассчитываем процент от суточной нормы
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == int(key)).first()
        daily_percentage = None
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = (nutrient_data['amount'] / float(daily_norm.amount)) * 100
        
        result[key] = NutrientInfo(
            name=nutrient_data['name'],
            unit_name=nutrient_data['unit_name'],
            amount=nutrient_data['amount'],
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
                    amount=0.0
                )
            total_nutrients[key].amount += nutrient.amount * item.quantity
        
        # Добавляем информацию о блюде
        dish_responses.append(DishNutrientsResponse(
            dish_id=dish.id,
            dish_name=dish.name,
            total_weight_g=100.0,  # стандартная порция 100г
            nutrients=dish_nutrients
        ))
    
    # Рассчитываем проценты для общих нутриентов
    for key, nutrient in total_nutrients.items():
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == int(key)).first()
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            nutrient.daily_percentage = (nutrient.amount / float(daily_norm.amount)) * 100
    
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
        order_nutrients = get_order_nutrients(db, order.id)
        
        # Суммируем нутриенты из этого заказа
        for key, nutrient in order_nutrients.total_nutrients.items():
            if key not in total_nutrients:
                total_nutrients[key] = NutrientInfo(
                    name=nutrient.name,
                    unit_name=nutrient.unit_name,
                    amount=0.0
                )
            total_nutrients[key].amount += nutrient.amount
    
    # Рассчитываем проценты
    for key, nutrient in total_nutrients.items():
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == int(key)).first()
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            nutrient.daily_percentage = (nutrient.amount / float(daily_norm.amount)) * 100
    
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
    dishes = db.query(Dish).all()
    
    menu: List[MenuDish] = []
    
    for dish in dishes:
        # Получаем нутриенты блюда
        nutrients = get_dish_nutrients(db, dish.id)
        
        # Собираем макронутриенты (калории, белки, жиры, углеводы)
        # Предполагаем, что id макронутриентов известны:
        # 1008 - Energy (kcal)
        # 1003 - Protein
        # 1004 - Total lipid (fat)
        # 1005 - Carbohydrate, by difference
        
        macros = MenuMacros(
            calories=float(nutrients.get('1008', NutrientInfo(name="", unit_name="", amount=0.0)).amount),
            protein=float(nutrients.get('1003', NutrientInfo(name="", unit_name="", amount=0.0)).amount),
            fat=float(nutrients.get('1004', NutrientInfo(name="", unit_name="", amount=0.0)).amount),
            carbs=float(nutrients.get('1005', NutrientInfo(name="", unit_name="", amount=0.0)).amount)
        )
        
        # Собираем микронутриенты
        micronutrients = {}
        for key, nutrient in nutrients.items():
            # Пропускаем макронутриенты
            if key in ['1008', '1003', '1004', '1005']:
                continue
                
            micronutrients[key] = MenuMicronutrient(
                name=nutrient.name,
                unit=nutrient.unit_name,
                value=nutrient.amount,
                coverage_percent=nutrient.daily_percentage or 0.0
            )
        
        # Генерируем рекомендации на основе нутриентов
        recommendations = []
        if macros.protein > 20:
            recommendations.append("Высокобелковое блюдо")
        if macros.fat < 10:
            recommendations.append("Низкое содержание жиров")
        
        # Проверяем микронутриенты
        for key, micro in micronutrients.items():
            if micro.coverage_percent > 50:
                recommendations.append(f"Богат {micro.name}")
        
        # Вычисляем оценку (простая эвристика)
        score = min(10, len(recommendations) + int(macros.protein / 5))
        
        menu.append(
            MenuDish(
                id=dish.id,
                name=dish.name,
                price=float(dish.price),
                description=dish.description,
                macros=macros,
                micronutrients=micronutrients,
                recommendations=recommendations[:3],  # максимум 3 рекомендации
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
    db.flush()  # получаем order.id
    
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
    producer.send('new_orders', {
        'order_id': order.id,
        'user_id': order.user_id,
        'total_price': float(total),
        'status': 'pending'
    })
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
