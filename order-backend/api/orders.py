from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared.database import get_db
from shared.models import Order, OrderItem
from shared.shared_models import  Dish

from api.schemas import OrderCreate, OrderResponse, OrderItemResponse
from core.kafka import produce_order_created

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    total = 0.0
    order_items_data = []

    for item in order_data.items:
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            raise HTTPException(404, f"Dish {item.dish_id} not found")

        item_total = float(dish.price) * item.quantity
        total += item_total
        order_items_data.append({
            "dish_id": item.dish_id,
            "quantity": item.quantity,
            "price": float(dish.price)
        })

    order = Order(user_id=order_data.user_id, total_price=total, status="pending")
    db.add(order)
    db.flush()

    for item_data in order_items_data:
        db.add(OrderItem(
            order_id=order.id,
            **item_data
        ))

    db.commit()
    db.refresh(order)

    # Kafka
    payload = {
        "order_id": order.id,
        "user_id": order.user_id,
        "total_price": total,
        "status": "pending",
    }
    produce_order_created(payload)

    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_price=total,
        created_at=order.created_at.isoformat(),
        items=[OrderItemResponse(id=i.id, dish_id=i.dish_id, quantity=i.quantity, price=float(i.price)) for i in items]
    )


@router.get("/{user_id}", response_model=List[OrderResponse])
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
