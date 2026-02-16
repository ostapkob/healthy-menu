import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import Delivery as DeliveryModel, Courier as CourierModel
from sqlalchemy.sql import func
from .schemas import (
    AssignDeliveryRequest,
    DeliveryResponse,
    # AssignDeliveryResponse
)

from shared.shared_models import (
    Order as OrderModel
)
from typing import List
from core.kafka import manager

router = APIRouter(
    prefix="/deliveries",
    tags=["deliveries"],
)


@router.post("/assign-delivery/")
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

@router.get("/my-deliveries/{courier_id}", response_model=List[DeliveryResponse])
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


@router.post("/update-delivery-status/{delivery_id}")
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
