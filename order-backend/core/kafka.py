import json
import os
from typing import Optional

from confluent_kafka import Producer

from core.config import settings


_producer: Optional[Producer] = None


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    # else:
    #     print(f"Delivered to {msg.topic()} [{msg.partition()}] @ {msg.offset()}")


def get_kafka_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer(
            {
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                # "enable.idempotence": True,   # рекомендуется включить в проде
                # "linger.ms": 5,
                # "batch.num.messages": 10000,
            }
        )
    return _producer


def produce_order_created(order_data: dict):
    producer = get_kafka_producer()
    payload = json.dumps(order_data).encode("utf-8")

    producer.produce(
        topic=settings.KAFKA_TOPIC,
        value=payload,
        callback=delivery_report,
    )
    producer.poll(0)
    producer.flush()  # можно убрать в высоконагруженном сервисе
