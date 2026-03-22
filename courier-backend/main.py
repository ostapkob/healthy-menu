from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from sqlalchemy.orm import Session
from core.kafka import manager, startup_kafka
from shared.models import Courier as CourierModel
from api import  couriers, deliveries, orders
from core.config import settings
from shared.logging import setup_logging, LoggingMiddleware, get_logger


app = FastAPI(title="Courier Service")

# Настройка логирования
setup_logging()

app.add_middleware(LoggingMiddleware)

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

app.include_router(couriers.router, prefix=settings.API_PREFIX)
app.include_router(deliveries.router, prefix=settings.API_PREFIX)
app.include_router(orders.router, prefix=settings.API_PREFIX)


@app.on_event("startup")
async def startup_event():
    await startup_kafka()
    logger = get_logger()
    logger.info("courier_service_started")

# === WebSocket Endpoint ===
@app.websocket("/api/v1/courier/ws/{courier_id}")
async def websocket_endpoint(websocket: WebSocket, courier_id: int, db: Session = Depends(get_db)):
    logger = get_logger()
    
    logger.info("websocket_connection_attempt", courier_id=courier_id)
    await manager.connect(websocket, courier_id)

    # Обновляем статус курьера на "available"
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if courier:
        logger.info("courier_status_updated", courier_id=courier_id, status="available")
        courier.status = "available"
        db.commit()

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug("websocket_message_received", courier_id=courier_id, data=data)
    except WebSocketDisconnect:
        logger.info("websocket_disconnected", courier_id=courier_id)
        manager.disconnect(courier_id)
        # Обновляем статус курьера на "offline"
        courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
        if courier:
            logger.info("courier_status_updated", courier_id=courier_id, status="offline")
            courier.status = "offline"
            db.commit()
