# admin/api/foods.py
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.database import get_db
from shared.models import Food, FoodRu, FoodCategory, FoodCategoryRu

router = APIRouter(prefix="/foods", tags=["foods"])


class FoodItem(BaseModel):
    fdc_id: int
    name: str              # лучшее доступное название (ru -> en)
    description_en: str    # оригинальное английское
    category_id: Optional[int] = None
    category_name: Optional[str] = None

    class Config:
        from_attributes = True


class FoodListResponse(BaseModel):
    items: List[FoodItem]
    total: int
    offset: int
    limit: int


@router.get("/", response_model=FoodListResponse)
def list_foods(
    q: Optional[str] = Query(None, description="Поиск по русскому/английскому названию"),
    category_id: Optional[int] = Query(None, description="Фильтр по ID категории"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """
    Список продуктов для формирования блюд.
    Возвращает FDC ID, русское/английское название и категорию.
    """

    # базовый запрос с join-ами для локализаций и категорий
    query = (
        db.query(
            Food.fdc_id,
            Food.description.label("description_en"),
            Food.food_category_id.label("category_id"),
            FoodRu.name_ru.label("name_ru"),
            FoodCategoryRu.name_ru.label("category_name_ru"),
            FoodCategory.description.label("category_name_en"),
        )
        .outerjoin(FoodRu, FoodRu.fdc_id == Food.fdc_id)
        .outerjoin(FoodCategory, FoodCategory.id == Food.food_category_id)
        .outerjoin(FoodCategoryRu, FoodCategoryRu.category_id == FoodCategory.id)
    )

    # фильтр по категории
    if category_id is not None:
        query = query.filter(Food.food_category_id == category_id)

    # фильтр по поисковой строке
    if q:
        pattern = f"%{q.lower()}%"
        query = query.filter(
            (FoodRu.name_ru.ilike(pattern))
            | (Food.description.ilike(pattern))
        )

    total = query.count()
    rows = query.offset(offset).limit(limit).all()

    items: List[FoodItem] = []
    for row in rows:
        # выбираем лучшее имя
        name = row.name_ru or row.description_en or f"Food #{row.fdc_id}"
        # категория: сначала ru, потом en
        category_name = row.category_name_ru or row.category_name_en

        items.append(
            FoodItem(
                fdc_id=row.fdc_id,
                name=name,
                description_en=row.description_en or "",
                category_id=row.category_id,
                category_name=category_name,
            )
        )

    return FoodListResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
    )
