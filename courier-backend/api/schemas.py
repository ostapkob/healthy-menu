from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# === Pydantic Models ===

class CourierResponse(BaseModel):
    id: int
    name: str
    status: str
    current_order_id: int | None
    photo_url: str | None

    class Config:
        from_attributes = True   # позволяет работать с ORM объектами (бывшее orm_mode)

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

    class Config:
        from_attributes = True

class UpdateCourierStatusRequest(BaseModel):
    status: str  # "online", "offline"


# /available-orders/
class AvailableOrderResponse(BaseModel):
    id: int
    user_id: int
    total_price: float
    status: str


# /assign-delivery
class AssignDeliveryResponse(BaseModel):
    ok: bool
    delivery_id: Optional[int] = None
    message: Optional[str] = None
