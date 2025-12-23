from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Ingredient as IngredientModel

router = APIRouter(prefix="/ingredients", tags=["ingredients"])


class IngredientCreate(BaseModel):
    name: str


class IngredientUpdate(BaseModel):
    name: Optional[str] = None


class IngredientResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[IngredientResponse])
def get_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(IngredientModel).offset(skip).limit(limit).all()


@router.post("/", response_model=IngredientResponse)
def create_ingredient(body: IngredientCreate, db: Session = Depends(get_db)):
    row = IngredientModel(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{ing_id}", response_model=IngredientResponse)
def update_ingredient(
    ing_id: int, body: IngredientUpdate, db: Session = Depends(get_db)
):
    row = db.query(IngredientModel).filter(IngredientModel.id == ing_id).first()
    if not row:
        raise HTTPException(404, "Ingredient not found")

    if body.name is not None:
        row.name = body.name

    db.commit()
    db.refresh(row)
    return row


@router.delete("/{ing_id}")
def delete_ingredient(ing_id: int, db: Session = Depends(get_db)):
    row = db.query(IngredientModel).filter(IngredientModel.id == ing_id).first()
    if not row:
        raise HTTPException(404, "Ingredient not found")
    db.delete(row)
    db.commit()
    return {"ok": True}

