from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from kafka import KafkaProducer
import json
import threading
from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from shared.models import Dish as DishModel, Order as OrderModel, OrderItem as OrderItemModel

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
            bootstrap_servers=['kafka:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    return producer

# === Pydantic Models ===

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

@app.get("/menu/", response_model=List[DishResponse])
def get_menu(db: Session = Depends(get_db)):
    dishes = db.query(DishModel).all()
    return dishes

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
            "price": dish.price
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

from fastapi.middleware.cors import CORSMiddleware

