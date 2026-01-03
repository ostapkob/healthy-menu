# admin/api/tech.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Dish, DishFood, Food

router = APIRouter(prefix="/tech", tags=["tech"])


class IngredientInput(BaseModel):
    food_id: int = Field(..., description="fdc_id из таблицы Food")
    amount_grams: float = Field(..., gt=0, description="Масса ингредиента в граммах")


class DishTechCreate(BaseModel):
    name: str = Field(..., description="Рабочее название блюда")
    ingredients: List[IngredientInput]


class IngredientTechResponse(BaseModel):
    id: int
    food_id: int
    amount_grams: float

    class Config:
        from_attributes = True


class DishTechResponse(BaseModel):
    id: int
    name: str
    ingredients: List[IngredientTechResponse]

    class Config:
        from_attributes = True


@router.post("/dishes/", response_model=DishTechResponse)
def create_dish_tech(data: DishTechCreate, db: Session = Depends(get_db)):
    # проверим, что такого имени блюда ещё нет
    exists = db.query(Dish).filter(Dish.name == data.name).first()
    if exists:
        raise HTTPException(status_code=400, detail="Dish with this name already exists")

    # создаём блюдо без цены, описания и фото
    dish = Dish(
        name=data.name,
        price=0,
        description=None,
        image_url=None,
    )
    db.add(dish)
    db.flush()  # чтобы получить dish.id

    # проверяем наличие ингредиентов
    food_ids = [ing.food_id for ing in data.ingredients]
    existing_food = db.query(Food.fdc_id).filter(Food.fdc_id.in_(food_ids)).all()
    existing_ids = {row.fdc_id for row in existing_food}
    missing = set(food_ids) - existing_ids
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Some food_ids do not exist: {sorted(missing)}",
        )

    # создаём связки DishFood
    dish_food_rows = [
        DishFood(
            dish_id=dish.id,
            food_id=ing.food_id,
            amount_grams=ing.amount_grams,
        )
        for ing in data.ingredients
    ]
    db.add_all(dish_food_rows)
    db.commit()
    db.refresh(dish)

    # загружаем ингредиенты через relationship для ответа
    db.refresh(dish)  # обновляем связи
    return DishTechResponse(
        id=dish.id,
        name=dish.name,
        ingredients=[
            IngredientTechResponse(
                id=ing.id,
                food_id=ing.food_id,
                amount_grams=ing.amount_grams,
            )
            for ing in dish.ingredients  # используем relationship Dish.ingredients
        ],
    )


@router.get("/dishes/{dish_id}", response_model=DishTechResponse)
def get_dish_tech(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).options().filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    return DishTechResponse(
        id=dish.id,
        name=dish.name,
        ingredients=[
            IngredientTechResponse(
                id=ing.id,
                food_id=ing.food_id,  # DishFood.food_id
                amount_grams=ing.amount_grams,
            )
            for ing in dish.ingredients  # Dish.ingredients -> DishFood
        ],
    )


class DishIngredientsUpdate(BaseModel):
    ingredients: List[IngredientInput]


@router.put("/dishes/{dish_id}/ingredients", response_model=DishTechResponse)
def update_dish_ingredients(
    dish_id: int, data: DishIngredientsUpdate, db: Session = Depends(get_db)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    # проверим food_id
    food_ids = [ing.food_id for ing in data.ingredients]
    existing_food = db.query(Food.fdc_id).filter(Food.fdc_id.in_(food_ids)).all()
    existing_ids = {row.fdc_id for row in existing_food}
    missing = set(food_ids) - existing_ids
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Some food_ids do not exist: {sorted(missing)}",
        )

    # удаляем старые связки
    db.query(DishFood).filter(DishFood.dish_id == dish_id).delete()

    # создаём новые
    new_rows = [
        DishFood(
            dish_id=dish_id,
            food_id=ing.food_id,
            amount_grams=ing.amount_grams,
        )
        for ing in data.ingredients
    ]
    db.add_all(new_rows)
    db.commit()
    db.refresh(dish)

    return DishTechResponse(
        id=dish.id,
        name=dish.name,
        ingredients=[
            IngredientTechResponse(
                id=row.id,
                food_id=row.food_id,
                amount_grams=row.amount_grams,
            )
            for row in new_rows
        ],
    )


@router.delete("/dishes/{dish_id}")
def delete_dish_tech(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    # каскадное удаление DishFood через ondelete
    db.delete(dish)
    db.commit()
    return {"ok": True}


@router.get("/dishes/", response_model=List[DishTechResponse])
def list_dishes_tech(db: Session = Depends(get_db)):
    """Получить список всех технологических карт"""
    dishes = db.query(Dish).all()
    return dishes
