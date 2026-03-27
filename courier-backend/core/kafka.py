import asyncio
import json
import os
import threading
import time
from typing import Dict, Optional

from confluent_kafka import Consumer, KafkaException
from fastapi import WebSocket, WebSocketDisconnect

from core.config import settings
from shared.models import Courier as CourierModel
from shared.database import get_db  # если нужно внутри websocket
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, courier_id: int):
        await websocket.accept()
        self.active_connections[courier_id] = websocket

    def disconnect(self, courier_id: int):
        self.active_connections.pop(courier_id, None)

    async def send_personal_message(self, message: str, courier_id: int):
        ws = self.active_connections.get(courier_id)
        if ws is not None:
            await ws.send_text(message)

    async def broadcast(self, message: str):
        for ws in list(self.active_connections.values()):
            try:
                await ws.send_text(message)
            except WebSocketDisconnect:
                pass


manager = ConnectionManager()


# Глобальная очередь (или можно передавать через dependency / app.state)
kafka_queue: asyncio.Queue = asyncio.Queue()


def create_kafka_consumer() -> Consumer:
    bootstrap = settings.KAFKA_BOOTSTRAP_SERVERS
    print(f"🔧 Creating Kafka consumer with bootstrap servers: {bootstrap!r}")
    return Consumer(
        {
            "bootstrap.servers": bootstrap,
            "group.id": "courier_group_v2",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
    )


def process_kafka_message(msg) -> Optional[dict]:
    """Возвращает данные заказа или None в случае ошибки"""
    if msg is None:
        return None
    if msg.error():
        print(f"⚠️ Kafka consumer error: {msg.error()}")
        return None

    try:
        order_data = json.loads(msg.value().decode("utf-8"))
        order_id = order_data.get("order_id")
        if order_id is not None:
            print(f"📢 Kafka: received new order {order_id}")
        return {"type": "new_order", "order_id": order_id}
    except Exception as e:
        print(f"⚠️ Ошибка декодирования сообщения: {e}")
        return None


def kafka_listener():
    """Kafka consumer в отдельном потоке"""
    global kafka_queue

    while True:
        try:
            consumer = create_kafka_consumer()
            print(f"📢 Subscribing to topic: {settings.TOPIC!r}")
            consumer.subscribe([settings.TOPIC])
            print("✅ Connected to Kafka successfully!")
            print(f"👂 Kafka слушает топик {settings.TOPIC}")

            while True:
                msg = consumer.poll(1.0)
                data = process_kafka_message(msg)
                if data is not None:
                    # Используем asyncio.run_coroutine_threadsafe для безопасной отправки в асинхронную очередь
                    try:
                        loop = asyncio.get_event_loop()
                        asyncio.run_coroutine_threadsafe(
                            kafka_queue.put(data),
                            loop
                        )
                    except RuntimeError:
                        # Event loop ещё не создан, пробуем получить или создать новый
                        print("⚠️ Event loop не доступен, пропускаем сообщение")

        except (KafkaException, json.JSONDecodeError) as e:
            print(f"Ошибка консьюмера: {e}")
            time.sleep(5)
        finally:
            consumer.close()


async def kafka_worker():
    """Асинхронный worker, рассылает сообщения всем подключённым курьерам"""
    while True:
        msg = await kafka_queue.get()
        await manager.broadcast(json.dumps(msg))
        print(f"📤 WS broadcast → order {msg['order_id']}")
        kafka_queue.task_done()


async def startup_kafka():
    """Вызывается в @app.on_event("startup")"""

    # Запускаем worker
    asyncio.create_task(kafka_worker())

    # Запускаем kafka consumer в отдельном потоке
    threading.Thread(target=kafka_listener, daemon=True).start()
    print("🧵 Kafka listener thread started")
