from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import (
    DishIngredient as DishIngredientModel,
    Dish as DishModel,
    Ingredient as IngredientModel,
)

router = APIRouter(prefix="/dish-ingredients", tags=["dish-ingredients"])


class DishIngredientCreate(BaseModel):
    dish_id: int
    ingredient_id: int
    amount_grams: float


class DishIngredientResponse(DishIngredientCreate):
    id: int

    class Config:
        from_attributes = True


class DishIngredientUpdate(BaseModel):
    id: Optional[int] = None
    dish_id: Optional[int] = None
    ingredient_id: Optional[int] = None
    amount_grams: Optional[float] = None


class DishIngredientBatchUpdate(BaseModel):
    updates: List[DishIngredientUpdate]
    deletions: List[int] = []


@router.get("/", response_model=List[DishIngredientResponse])
def get_dish_ingredients(
    dish_id: Optional[int] = None,
    ingredient_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(DishIngredientModel)
    if dish_id:
        query = query.filter(DishIngredientModel.dish_id == dish_id)
    if ingredient_id:
        query = query.filter(DishIngredientModel.ingredient_id == ingredient_id)
    return query.all()


@router.post("/", response_model=DishIngredientResponse)
def create_dish_ingredient(item: DishIngredientCreate, db: Session = Depends(get_db)):
    db_item = DishIngredientModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.put("/{item_id}", response_model=DishIngredientResponse)
def update_dish_ingredient(
    item_id: int, item: DishIngredientUpdate, db: Session = Depends(get_db)
):
    db_item = (
        db.query(DishIngredientModel)
        .filter(DishIngredientModel.id == item_id)
        .first()
    )
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.dict(exclude_unset=True).items():
        if key == "id":
            continue
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_dish_ingredient(item_id: int, db: Session = Depends(get_db)):
    db_item = (
        db.query(DishIngredientModel)
        .filter(DishIngredientModel.id == item_id)
        .first()
    )
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}


@router.get("/enhanced/")
def get_dish_ingredients_enhanced(
    dish_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    query = db.query(
        DishIngredientModel.id,
        DishIngredientModel.dish_id,
        DishModel.name.label("dish_name"),
        DishIngredientModel.ingredient_id,
        IngredientModel.name.label("ingredient_name"),
        DishIngredientModel.amount_grams,
    ).join(DishModel, DishIngredientModel.dish_id == DishModel.id).join(
        IngredientModel, DishIngredientModel.ingredient_id == IngredientModel.id
    )

    if dish_id:
        query = query.filter(DishIngredientModel.dish_id == dish_id)

    results = query.all()

    return [
        {
            "id": row.id,
            "dish_id": row.dish_id,
            "dish_name": row.dish_name,
            "ingredient_id": row.ingredient_id,
            "ingredient_name": row.ingredient_name,
            "amount_grams": row.amount_grams,
        }
        for row in results
    ]


@router.get("/stats/")
def get_dish_ingredients_stats(db: Session = Depends(get_db)):
    total = db.query(DishIngredientModel).count()
    dishes_count = (
        db.query(func.count(func.distinct(DishIngredientModel.dish_id))).scalar()
    )
    ingredients_count = (
        db.query(func.count(func.distinct(DishIngredientModel.ingredient_id))).scalar()
    )

    top_dishes_query = (
        db.query(
            DishModel.name,
            func.count(DishIngredientModel.id).label("ingredient_count"),
        )
        .join(DishIngredientModel, DishModel.id == DishIngredientModel.dish_id)
        .group_by(DishModel.id, DishModel.name)
        .order_by(func.count(DishIngredientModel.id).desc())
        .limit(5)
        .all()
    )
    top_dishes = [{"name": row[0], "count": row[1]} for row in top_dishes_query]

    return {
        "total_entries": total,
        "unique_dishes": dishes_count,
        "unique_ingredients": ingredients_count,
        "top_dishes": top_dishes,
    }


@router.put("/batch/")
def update_dish_ingredients_batch(
    batch: DishIngredientBatchUpdate,
    db: Session = Depends(get_db),
):
    results = []

    for update_data in batch.updates:
        if not update_data.id:
            continue
        item = (
            db.query(DishIngredientModel)
            .filter(DishIngredientModel.id == update_data.id)
            .first()
        )
        if item:
            for key, value in update_data.dict(
                exclude_unset=True, exclude={"id"}
            ).items():
                if value is not None:
                    setattr(item, key, value)
            results.append({"id": item.id, "action": "updated"})

    for item_id in batch.deletions:
        item = (
            db.query(DishIngredientModel)
            .filter(DishIngredientModel.id == item_id)
            .first()
        )
        if item:
            db.delete(item)
            results.append({"id": item_id, "action": "deleted"})

    db.commit()
    return {"results": results}

