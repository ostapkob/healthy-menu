# admin/api/dishes.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Dish

router = APIRouter(prefix="/dishes", tags=["admin-dishes"])


class DishAdminListItem(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    image_url: Optional[str]

    class Config:
        from_attributes = True


class DishAdminDetail(DishAdminListItem):
    pass


class DishAdminUpdate(BaseModel):
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


@router.get("/", response_model=List[DishAdminListItem])
def list_dishes(db: Session = Depends(get_db)):
    return db.query(Dish).order_by(Dish.id).all()


@router.get("/{dish_id}", response_model=DishAdminDetail)
def get_dish_admin(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.put("/{dish_id}", response_model=DishAdminDetail)
def update_dish_admin(
    dish_id: int, data: DishAdminUpdate, db: Session = Depends(get_db)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dish, key, value)

    db.commit()
    db.refresh(dish)
    return dish

