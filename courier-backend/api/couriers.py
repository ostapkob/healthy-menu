from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import Courier as CourierModel
from .schemas import CourierResponse, UpdateCourierStatusRequest

router = APIRouter(
    prefix="/couriers",
    tags=["couriers"],
)


@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(courier_id: int, db: Session = Depends(get_db)):
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if not courier:
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier

@router.put("/{courier_id}/status")
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

