from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared.database import get_db

router = APIRouter(prefix="/coverage-report", tags=["reports"])


class CoverageResponse(BaseModel):
    dish_name: str
    organ_name: str
    nutrient_name: str
    daily_requirement_amount: float
    daily_requirement_unit: str
    nutrient_in_dish_amount: float
    nutrient_in_dish_unit: str
    coverage_percentage: float


@router.get("/", response_model=List[CoverageResponse])
def get_coverage_report(
    dish_id: Optional[int] = None,
    organ_id: Optional[int] = None,
    nutrient_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    base_sql = """
    SELECT
        d.name AS dish_name,
        o.name AS organ_name,
        n.name AS nutrient_name,
        dnr.amount AS daily_requirement_amount,
        n.unit AS daily_requirement_unit,
        COALESCE(SUM(di.amount_grams / 100 * inc.content_per_100g), 0) AS nutrient_in_dish_amount,
        n.unit AS nutrient_in_dish_unit,
        CASE
            WHEN dnr.amount > 0 THEN (SUM(di.amount_grams / 100 * inc.content_per_100g) / dnr.amount) * 100
            ELSE 0
        END AS coverage_percentage
    FROM dishes d
    JOIN dish_ingredients di ON d.id = di.dish_id
    JOIN ingredients ing ON di.ingredient_id = ing.id
    JOIN ingredient_nutrient_contents inc ON ing.id = inc.ingredient_id
    JOIN nutrients n ON inc.nutrient_id = n.id
    JOIN nutrient_organ_benefits nob ON n.id = nob.nutrient_id
    JOIN organs o ON nob.organ_id = o.id
    JOIN daily_nutrient_requirements dnr
        ON n.id = dnr.nutrient_id AND dnr.age_group = 'взрослый'
    WHERE 1=1
    """

    params = {}

    if dish_id:
        base_sql += " AND d.id = :dish_id"
        params["dish_id"] = dish_id

    if organ_id:
        base_sql += " AND o.id = :organ_id"
        params["organ_id"] = organ_id

    if nutrient_id:
        base_sql += " AND n.id = :nutrient_id"
        params["nutrient_id"] = nutrient_id

    base_sql += """
    GROUP BY d.id, d.name, o.id, o.name, n.id, n.name, dnr.amount, n.unit
    ORDER BY coverage_percentage DESC;
    """

    result = db.execute(text(base_sql), params).fetchall()

    return [
        CoverageResponse(
            dish_name=row.dish_name,
            organ_name=row.organ_name,
            nutrient_name=row.nutrient_name,
            daily_requirement_amount=row.daily_requirement_amount,
            daily_requirement_unit=row.daily_requirement_unit,
            nutrient_in_dish_amount=row.nutrient_in_dish_amount,
            nutrient_in_dish_unit=row.nutrient_in_dish_unit,
            coverage_percentage=row.coverage_percentage,
        )
        for row in result
    ]

