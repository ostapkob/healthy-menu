from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import asyncio
import json
from kafka import KafkaConsumer
import threading
import time
from sqlalchemy.sql import func
from sqlalchemy.sql import func  # <-- добавлен импорт


from shared.database import get_db
from shared.models import Courier as CourierModel, Delivery as DeliveryModel, Order as OrderModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Courier Service")

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

# === WebSocket Manager ===

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, courier_id: int):
        await websocket.accept()
        self.active_connections[courier_id] = websocket

    def disconnect(self, courier_id: int):
        if courier_id in self.active_connections:
            del self.active_connections[courier_id]

    async def send_personal_message(self, message: str, courier_id: int):
        websocket = self.active_connections.get(courier_id)
        if websocket:
            await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# === Kafka Consumer Thread ===
def kafka_listener():
    while True:
        try:
            consumer = KafkaConsumer(
                'new_orders',
                bootstrap_servers=['kafka:9092'],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                group_id='courier_group'
            )
            print("Connected to Kafka successfully!")
            break
        except Exception as e:
            print(f"Failed to connect to Kafka: {e}. Retrying in 5 seconds...")
            time.sleep(5)

    for message in consumer:
        order_data = message.value
        order_id = order_data['order_id']

        # Отправляем всем доступным курьерам через WebSocket
        asyncio.run(
            manager.broadcast(
                json.dumps({"type": "new_order", "order_id": order_id})
            )
        )

# Запускаем в отдельном потоке
threading.Thread(target=kafka_listener, daemon=True).start()

# === Pydantic Models ===

class CourierResponse(BaseModel):
    id: int
    name: str
    status: str
    current_order_id: int | None

class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    courier_id: int
    status: str

class AssignDeliveryRequest(BaseModel):
    courier_id: int
    order_id: int
   
class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    status: str
    assigned_at: str
    picked_up_at: str | None
    delivered_at: str | None


# === WebSocket Endpoint ===

@app.websocket("/ws/{courier_id}")
async def websocket_endpoint(websocket: WebSocket, courier_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket, courier_id)

    # Обновляем статус курьера на "available"
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if courier:
        courier.status = "available"
        db.commit()

    try:
        while True:
            data = await websocket.receive_text()
            # Курьер может отправить сообщение (например, "I'm ready")
            # Пока не обрабатываем
    except WebSocketDisconnect:
        manager.disconnect(courier_id)
        # Обновляем статус курьера на "offline"
        courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
        if courier:
            courier.status = "offline"
            db.commit()

# === API Endpoints ===

@app.get("/couriers/", response_model=List[CourierResponse])
def get_couriers(db: Session = Depends(get_db)):
    couriers = db.query(CourierModel).all()
    return [
        CourierResponse(
            id=c.id,
            name=c.name,
            status=c.status,
            current_order_id=c.current_order_id
        )
        for c in couriers
    ]

@app.get("/available-orders/", response_model=List[dict])
def get_available_orders(db: Session = Depends(get_db)):
    # Найти заказы, которые находятся в активной доставке
    active_delivery_order_ids = db.query(DeliveryModel.order_id).filter(
        DeliveryModel.status != "delivered"
    ).all()

    active_ids = {row[0] for row in active_delivery_order_ids}

    # 1. Не в активной доставке и не имеют статус "delivered" в таблице orders
    orders = db.query(OrderModel).filter(
        OrderModel.id.notin_(active_ids),
        OrderModel.status != "delivered"
    ).all()

    return [
        {
            "id": o.id,
            "user_id": o.user_id,
            "total_price": float(o.total_price),
            "status": o.status
        }
        for o in orders
    ]

@app.post("/assign-delivery/")
async def assign_delivery(req: AssignDeliveryRequest, db: Session = Depends(get_db)):
    # Проверяем, что курьер свободен
    courier = db.query(CourierModel).filter(CourierModel.id == req.courier_id).first()
    if not courier or courier.status == "off_line":
        raise HTTPException(status_code=400, detail="Courier is not available")

    # Проверяем, что заказ не занят
    existing_delivery = db.query(DeliveryModel).filter(
        DeliveryModel.order_id == req.order_id,
        DeliveryModel.status != "delivered"
    ).first()

    if existing_delivery:
        raise HTTPException(status_code=400, detail="Order is already assigned")

    # Создаём доставку
    delivery = DeliveryModel(
        order_id=req.order_id,
        courier_id=req.courier_id,
        status="assigned"
    )
    db.add(delivery)

    # Обновляем статус курьера
    courier.status = "going_to_pickup"
    courier.current_order_id = req.order_id

    db.commit()

    await manager.send_personal_message(
        json.dumps({"type": "order_assigned", "order_id": req.order_id}),
        req.courier_id
    )

    return {"ok": True}

@app.post("/update-delivery-status/{delivery_id}")
async def update_delivery_status(
    delivery_id: int,
    status: str,  # picked_up, on_way, delivered
    db: Session = Depends(get_db)
):
    delivery = db.query(DeliveryModel).filter(DeliveryModel.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    delivery.status = status

    if status == "picked_up":
        delivery.picked_up_at = func.now()
    elif status == "delivered":
        delivery.delivered_at = func.now()

    # ✅ Обновляем статус заказа в таблице `orders`
    order = db.query(OrderModel).filter(OrderModel.id == delivery.order_id).first()
    if order:
        print(order, status)
        order.status = status

    # Обновляем статус курьера
    courier = db.query(CourierModel).filter(CourierModel.id == delivery.courier_id).first()
    if courier:
        if status == "delivered":
            courier.status = "available"
            courier.current_order_id = None
        elif status == "picked_up":
            courier.status = "delivering"

    db.commit()
    return {"ok": True}

@app.get("/my-deliveries/{courier_id}", response_model=List[DeliveryResponse])
def get_my_deliveries(courier_id: int, db: Session = Depends(get_db)):
    deliveries = db.query(DeliveryModel).filter(
        DeliveryModel.courier_id == courier_id,
        DeliveryModel.status != "delivered"  # не показываем завершённые
    ).all()

    return [
        DeliveryResponse(
            id=d.id,
            order_id=d.order_id,
            status=d.status,
            assigned_at=d.assigned_at.isoformat(),
            picked_up_at=d.picked_up_at.isoformat() if d.picked_up_at else None,
            delivered_at=d.delivered_at.isoformat() if d.delivered_at else None
        )
        for d in deliveries
    ]

