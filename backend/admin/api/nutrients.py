from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import (
    Nutrient as NutrientModel,
    IngredientNutrientContent as INC,
    Ingredient as IngredientModel,
)

router = APIRouter(tags=["nutrients"])


class NutrientCreate(BaseModel):
    name: str
    short_name: str
    type: str
    unit: str


class NutrientUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    type: Optional[str] = None
    unit: Optional[str] = None


class NutrientResponse(BaseModel):
    id: int
    name: str
    short_name: str
    type: str
    unit: str

    class Config:
        from_attributes = True


class NutrientContentCreate(BaseModel):
    ingredient_id: int
    nutrient_id: int
    content_per_100g: float


class NutrientContentUpdate(BaseModel):
    ingredient_id: Optional[int] = None
    nutrient_id: Optional[int] = None
    content_per_100g: Optional[float] = None


class NutrientContentResponse(NutrientContentCreate):
    id: int
    ingredient_name: str
    nutrient_name: str


@router.get("/nutrients/", response_model=List[NutrientResponse])
def get_nutrients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(NutrientModel).offset(skip).limit(limit).all()


@router.post("/nutrients/", response_model=NutrientResponse)
def create_nutrient(body: NutrientCreate, db: Session = Depends(get_db)):
    row = NutrientModel(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/nutrients/{nut_id}", response_model=NutrientResponse)
def update_nutrient(
    nut_id: int, body: NutrientUpdate, db: Session = Depends(get_db)
):
    row = db.query(NutrientModel).filter(NutrientModel.id == nut_id).first()
    if not row:
        raise HTTPException(404, "Nutrient not found")

    for k, v in body.dict(exclude_unset=True).items():
        setattr(row, k, v)

    db.commit()
    db.refresh(row)
    return row


@router.delete("/nutrients/{nut_id}")
def delete_nutrient(nut_id: int, db: Session = Depends(get_db)):
    row = db.query(NutrientModel).filter(NutrientModel.id == nut_id).first()
    if not row:
        raise HTTPException(404, "Nutrient not found")
    db.delete(row)
    db.commit()
    return {"ok": True}


@router.get("/nutrient-contents/", response_model=List[NutrientContentResponse])
def get_contents(db: Session = Depends(get_db)):
    rows = (
        db.query(
            INC.id,
            INC.ingredient_id,
            INC.nutrient_id,
            INC.content_per_100g,
            IngredientModel.name.label("ingredient_name"),
            NutrientModel.name.label("nutrient_name"),
        )
        .join(IngredientModel)
        .join(NutrientModel)
        .all()
    )

    return [
        NutrientContentResponse(
            id=row.id,
            ingredient_id=row.ingredient_id,
            nutrient_id=row.nutrient_id,
            content_per_100g=row.content_per_100g,
            ingredient_name=row.ingredient_name,
            nutrient_name=row.nutrient_name,
        )
        for row in rows
    ]


@router.post("/nutrient-contents/", response_model=NutrientContentResponse)
def create_nutrient_content(
    body: NutrientContentCreate, db: Session = Depends(get_db)
):
    row = INC(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)

    q = (
        db.query(
            INC.id,
            INC.ingredient_id,
            INC.nutrient_id,
            INC.content_per_100g,
            IngredientModel.name.label("ingredient_name"),
            NutrientModel.name.label("nutrient_name"),
        )
        .join(IngredientModel)
        .join(NutrientModel)
        .filter(INC.id == row.id)
        .first()
    )

    return NutrientContentResponse(
        id=q.id,
        ingredient_id=q.ingredient_id,
        nutrient_id=q.nutrient_id,
        content_per_100g=q.content_per_100g,
        ingredient_name=q.ingredient_name,
        nutrient_name=q.nutrient_name,
    )


@router.put("/nutrient-contents/{cid}", response_model=NutrientContentResponse)
def update_nutrient_content(
    cid: int, body: NutrientContentUpdate, db: Session = Depends(get_db)
):
    row = db.query(INC).filter(INC.id == cid).first()
    if not row:
        raise HTTPException(404, "Content row not found")

    for k, v in body.dict(exclude_unset=True).items():
        setattr(row, k, v)

    db.commit()
    db.refresh(row)

    q = (
        db.query(
            INC.id,
            INC.ingredient_id,
            INC.nutrient_id,
            INC.content_per_100g,
            IngredientModel.name.label("ingredient_name"),
            NutrientModel.name.label("nutrient_name"),
        )
        .join(IngredientModel)
        .join(NutrientModel)
        .filter(INC.id == cid)
        .first()
    )

    return NutrientContentResponse(
        id=q.id,
        ingredient_id=q.ingredient_id,
        nutrient_id=q.nutrient_id,
        content_per_100g=q.content_per_100g,
        ingredient_name=q.ingredient_name,
        nutrient_name=q.nutrient_name,
    )


@router.delete("/nutrient-contents/{cid}")
def delete_nutrient_content(cid: int, db: Session = Depends(get_db)):
    row = db.query(INC).filter(INC.id == cid).first()
    if not row:
        raise HTTPException(404, "Content row not found")
    db.delete(row)
    db.commit()
    return {"ok": True}

