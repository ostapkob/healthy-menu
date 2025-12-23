from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Dish as DishModel

router = APIRouter(prefix="/dishes", tags=["dishes"])


class DishCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None


class DishUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


class DishFullResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        from_attributes = True


@router.get("/", response_model=List[DishFullResponse])
def get_dishes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(DishModel).offset(skip).limit(limit).all()


@router.get("/{dish_id}", response_model=DishFullResponse)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.post("/", response_model=DishFullResponse)
def create_dish(dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = DishModel(**dish.dict())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.put("/{dish_id}", response_model=DishFullResponse)
def update_dish(dish_id: int, dish_update: DishUpdate, db: Session = Depends(get_db)):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    for key, value in dish_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_dish, key, value)

    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.delete("/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    db.delete(db_dish)
    db.commit()
    return {"ok": True}

