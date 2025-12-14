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
import os

from shared.database import get_db
from shared.models import Courier as CourierModel, Delivery as DeliveryModel, Order as OrderModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Courier Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",          
        "ws://localhost:5173",            
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

# === WebSocket Manager ===

class ConnectionManager:
    def __init__(self):
        # courier_id -> WebSocket
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
        for connection in list(self.active_connections.values()):
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                # Можно удалить соединение, если нужно
                pass


manager = ConnectionManager()

# === Глобальные объекты для Kafka → asyncio ===
app.kafka_queue: asyncio.Queue = asyncio.Queue()
event_loop: asyncio.AbstractEventLoop | None = None


# === Kafka Consumer Thread ===

def kafka_listener():
    global event_loop
    print("🔧 Запускаем Kafka-листенер...")

    while True:
        try:
            consumer = KafkaConsumer(
                "new_orders",
                bootstrap_servers=[os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")],
                value_deserializer=lambda m: json.loads(m.decode("utf-8")),
                auto_offset_reset="earliest",  # для дебага; потом можно поменять
                group_id="courier_group_v2",
                enable_auto_commit=True,
            )
            print("✅ Connected to Kafka successfully!")
            print("👂 Kafka слушает топик 'new_orders'...")

            for message in consumer:
                order_data = message.value
                order_id = order_data["order_id"]
                print(f"📢 Kafka: received new order {order_id}")

                if event_loop is not None:
                    # Потокобезопасно кладём сообщение в asyncio.Queue основного цикла
                    event_loop.call_soon_threadsafe(
                        app.kafka_queue.put_nowait,
                        {"type": "new_order", "order_id": order_id},
                    )
                else:
                    print("⚠️ event_loop is None, не могу положить сообщение в очередь")

        except Exception as e:
            print("Ошибка консьюмера", e)
            time.sleep(5)


# === Запуск фонового worker'а и сохранение event loop ===

@app.on_event("startup")
async def start_kafka_worker():
    global event_loop
    event_loop = asyncio.get_event_loop()

    async def worker():
        while True:
            msg = await app.kafka_queue.get()
            await manager.broadcast(json.dumps(msg))
            print(f"📤 WebSocket: broadcasted order {msg['order_id']}")

    asyncio.create_task(worker())

    # Запускаем Kafka-листенер в отдельном потоке
    threading.Thread(target=kafka_listener, daemon=True).start()
    print("🧵 Kafka-листенер запущен в потоке")

# === Pydantic Models ===

class CourierResponse(BaseModel):
    id: int
    name: str
    status: str
    current_order_id: int | None
    photo_url: str | None

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

class UpdateCourierStatusRequest(BaseModel):
    status: str  # "online", "offline"

# === WebSocket Endpoint ===
@app.websocket("/ws/{courier_id}")
async def websocket_endpoint(websocket: WebSocket, courier_id: int, db: Session = Depends(get_db)):
    print(f"✅ WebSocket connection attempt for courier_id: {courier_id}")
    await manager.connect(websocket, courier_id)

    # Обновляем статус курьера на "available"
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if courier:
        print(f"🔄 Updating courier {courier_id} status to 'available'")
        courier.status = "available"
        db.commit()

    try:
        while True:
            data = await websocket.receive_text()
            print(f"💬 Received: {data}")
    except WebSocketDisconnect:
        print(f"⚠️ WebSocket disconnected for courier_id: {courier_id}")
        manager.disconnect(courier_id)
        # Обновляем статус курьера на "offline"
        courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
        if courier:
            print(f"🔄 Updating courier {courier_id} status to 'offline'")
            courier.status = "offline"
            db.commit()

# === API Endpoints ===

@app.get("/couriers/{courier_id}", response_model=CourierResponse)
def get_courier(courier_id: int, db: Session = Depends(get_db)):
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier

@app.put("/couriers/{courier_id}/status")
def update_courier_status(
    courier_id: int,
    req: UpdateCourierStatusRequest,
    db: Session = Depends(get_db)
):
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")

    # Проверяем, что статус допустим
    allowed_statuses = ["online", "offline", "available", "delivering", "going_to_pickup"]
    if req.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")

    courier.status = req.status
    db.commit()

    # Если offline — отключаем WebSocket (если подключён)
    if req.status == "offline":
        manager.disconnect(courier_id)

    return {"ok": True}

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
def get_my_deliveries(
    courier_id: int,
    history: bool = False,  # ← новый параметр
    db: Session = Depends(get_db)
):
    query = db.query(DeliveryModel).filter(DeliveryModel.courier_id == courier_id)

    if history:
        # Показываем **все** доставки (включая завершённые)
        deliveries = query.all()
    else:
        # Только **незавершённые**
        deliveries = query.filter(DeliveryModel.status != "delivered").all()

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
