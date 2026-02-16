from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import Delivery as DeliveryModel
from .schemas import AvailableOrderResponse
from typing import List

from shared.shared_models import (
    Order as OrderModel
)

router = APIRouter(
    prefix="/orders",
    tags=["orders"],
)


@router.get("/available-orders/", response_model=List[dict])
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
