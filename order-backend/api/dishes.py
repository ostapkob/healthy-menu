from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from shared.database import get_db
from shared.shared_models import Dish, DishFood

from api.schemas import (
    DishNutrientsResponse, MenuDish, DishResponse,
    MenuMacros, MenuMicronutrient, NutrientInfo
)
from .nutrients import get_dish_nutrients, get_nutrients_with_translation  # ← вынеси функции

router = APIRouter(prefix="/dishes", tags=["dishes"])


@router.get("/{dish_id}/nutrients", response_model=DishNutrientsResponse)
def get_dish_nutrients_endpoint(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(404, "Dish not found")

    nutrients = get_dish_nutrients(db, dish_id)

    dish_foods = db.query(DishFood).filter(DishFood.dish_id == dish_id).all()
    total_weight = sum(df.amount_grams for df in dish_foods) or 1.0

    return DishNutrientsResponse(
        dish_id=dish.id,
        dish_name=dish.name,
        total_weight_g=total_weight,
        nutrients=nutrients
    )


@router.get("/", response_model=List[DishResponse])
def get_all_dishes(db: Session = Depends(get_db)):
    dishes = db.query(Dish).all()
    return [DishResponse(id=d.id, name=d.name, price=float(d.price)) for d in dishes]


@router.get("/menu/", response_model=List[MenuDish])
def get_menu(db: Session = Depends(get_db)):
    """Получить меню с нутриентами"""
    dishes = db.query(Dish).all()

    menu: List[MenuDish] = []

    for dish in dishes:
        # Получаем нутриенты блюда
        dish_nutrients = get_dish_nutrients(db, dish.id)

        # Извлекаем макронутриенты
        protein = dish_nutrients.get('1003', NutrientInfo(name='', unit_name='', amount=0)).amount
        fat = dish_nutrients.get('1004', NutrientInfo(name='', unit_name='', amount=0)).amount
        carbs = dish_nutrients.get('1005', NutrientInfo(name='', unit_name='', amount=0)).amount

        # Рассчитываем калории: 4*белки + 9*жиры + 4*углеводы
        calories = protein * 4 + fat * 9 + carbs * 4

        # Макронутриенты
        macros = MenuMacros(
            calories=calories,
            protein=protein,
            fat=fat,
            carbs=carbs
        )

        # Собираем микронутриенты (все кроме макро)
        micronutrients = {}
        for nutrient_id_str, nutrient in dish_nutrients.items():
            if nutrient_id_str not in ['1003', '1004', '1005']:
                micronutrients[nutrient_id_str] = MenuMicronutrient(
                    name=nutrient.name,
                    unit=nutrient.unit_name,
                    value=nutrient.amount,
                    coverage_percent=nutrient.daily_percentage or 0
                )

        # Генерируем рекомендации
        recommendations = []

        if protein > 15:
            recommendations.append("Богато белком")
        if fat < 5:
            recommendations.append("Низкое содержание жиров")
        if carbs > 30:
            recommendations.append("Хороший источник энергии")

        # Рекомендации по микронутриентам
        for nutrient_id_str, nutrient in dish_nutrients.items():
            if nutrient.daily_percentage and nutrient.daily_percentage > 20:
                recommendations.append(f"Содержит {nutrient.name}")

        # Убираем дубликаты и ограничиваем количество
        recommendations = list(dict.fromkeys(recommendations))[:3]

        # Вычисляем оценку
        score = 5

        if protein > 15:
            score += 1
        if fat < 10:
            score += 1

        nutrient_count = len(micronutrients)
        if nutrient_count > 5:
            score += 1
        if nutrient_count > 10:
            score += 1

        score = min(10, max(1, score))

        menu.append(
            MenuDish(
                id=dish.id,
                name=dish.name,
                price=float(dish.price),
                description=dish.description,
                macros=macros,
                micronutrients=micronutrients,
                recommendations=recommendations,
                score=score,
                image_url=dish.image_url,
            )
        )

    return menu
