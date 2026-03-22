from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from shared.database import get_db
from shared.models import Courier as CourierModel
from .schemas import CourierResponse, UpdateCourierStatusRequest
from shared.logging import get_logger

logger = get_logger()

router = APIRouter(
    prefix="/couriers",
    tags=["couriers"],
)


@router.get("/{courier_id}", response_model=CourierResponse)
def get_courier(courier_id: int, db: Session = Depends(get_db)):
    logger = get_logger()
    
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if not courier:
        logger.warning("courier_not_found", courier_id=courier_id)
        raise HTTPException(status_code=404, detail="Courier not found")
    return courier

@router.put("/{courier_id}/status")
def update_courier_status(
    courier_id: int,
    req: UpdateCourierStatusRequest,
    db: Session = Depends(get_db)
):
    logger = get_logger()
    
    courier = db.query(CourierModel).filter(CourierModel.id == courier_id).first()
    if not courier:
        logger.warning("courier_not_found", courier_id=courier_id)
        raise HTTPException(status_code=404, detail="Courier not found")

    # Проверяем, что статус допустим
    allowed_statuses = ["online", "offline", "available", "delivering", "going_to_pickup"]
    if req.status not in allowed_statuses:
        logger.warning("invalid_status", courier_id=courier_id, status=req.status)
        raise HTTPException(status_code=400, detail="Invalid status")

    courier.status = req.status
    db.commit()
    
    logger.info("courier_status_updated", courier_id=courier_id, status=req.status)

    # Если offline — отключаем WebSocket (если подключён)
    if req.status == "offline":
        manager.disconnect(courier_id)

    return {"ok": True}

