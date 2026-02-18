from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict

from shared.database import get_db
from shared.models import (
    Order, OrderItem, Nutrient,
    NutrientRu, FoodNutrient, DailyNorm)
from shared.shared_models import Dish, DishFood

from core.kafka import produce_order_created

from api.schemas import (
    DishNutrientsResponse,
    NutrientInfo,
    OrderNutrientsResponse,
    UserNutrientsResponse
)

router = APIRouter(prefix="/nutrients", tags=["nutrients"])


def get_dish_nutrients(db: Session, dish_id: int) -> Dict[str, NutrientInfo]:
    """
    Получить все нутриенты для блюда с расчетом на 100г
    Используем только нутриенты из nutrient_ru
    """
    # Получаем нутриенты с русским переводом
    nutrients_map = get_nutrients_with_translation(db)

    # Получаем состав блюда
    dish_foods = db.query(DishFood).filter(DishFood.dish_id == dish_id).all()

    # Общий вес блюда
    total_weight = sum(df.amount_grams for df in dish_foods) or 1

    # Собираем нутриенты
    nutrient_totals = {}

    for dish_food in dish_foods:
        # Коэффициент для пересчета на 100г блюда
        factor = dish_food.amount_grams / total_weight

        # Получаем нутриенты для этого продукта
        food_nutrients = db.query(FoodNutrient).filter(
            FoodNutrient.fdc_id == dish_food.food_id,
            FoodNutrient.nutrient_id.in_(nutrients_map.keys())
        ).all()

        for food_nutrient in food_nutrients:
            nutrient_id = food_nutrient.nutrient_id
            if nutrient_id not in nutrient_totals:
                nutrient_totals[nutrient_id] = 0.0

            # Добавляем нутриент с учетом веса ингредиента
            nutrient_totals[nutrient_id] += float(food_nutrient.amount or 0) * factor

    # Преобразуем в NutrientInfo
    result = {}
    for nutrient_id, amount in nutrient_totals.items():
        if nutrient_id not in nutrients_map:
            continue

        nutrient_info = nutrients_map[nutrient_id]

        # Рассчитываем процент от суточной нормы
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == nutrient_id).first()
        daily_percentage = None

        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = int(round((amount / float(daily_norm.amount)) * 100))

        # Округляем значение до целого
        rounded_amount = int(round(amount))

        result[str(nutrient_id)] = NutrientInfo(
            name=nutrient_info['name'],
            unit_name=nutrient_info['unit_name'].lower(),
            amount=rounded_amount,
            daily_percentage=daily_percentage
        )

    return result


def get_order_nutrients(db: Session, order_id: int) -> OrderNutrientsResponse:
    """
    Получить нутриенты для заказа
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()

    total_nutrients = {}
    dish_responses = []

    for item in order_items:
        # Получаем нутриенты для блюда
        dish = db.query(Dish).filter(Dish.id == item.dish_id).first()
        if not dish:
            continue

        dish_nutrients = get_dish_nutrients(db, item.dish_id)

        # Умножаем на количество порций
        for key, nutrient in dish_nutrients.items():
            if key not in total_nutrients:
                total_nutrients[key] = NutrientInfo(
                    name=nutrient.name,
                    unit_name=nutrient.unit_name,
                    amount=0,
                    daily_percentage=0
                )

            # Обновляем значения
            total_nutrients[key].amount += nutrient.amount * item.quantity


        # Добавляем информацию о блюде
        dish_responses.append(DishNutrientsResponse(
            dish_id=dish.id,
            dish_name=dish.name,
            total_weight_g=100.0,
            nutrients=dish_nutrients
        ))

    # Рассчитываем проценты для общих нутриентов
    nutrients_map = get_nutrients_with_translation(db)

    for key, nutrient in total_nutrients.items():
        nutrient_id = int(key)

        # Рассчитываем процент от суточной нормы
        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == nutrient_id).first()
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = int(round((nutrient.amount / float(daily_norm.amount)) * 100))
            nutrient.daily_percentage = daily_percentage

    return OrderNutrientsResponse(
        order_id=order_id,
        total_nutrients=total_nutrients,
        dishes=dish_responses
    )


def get_user_total_nutrients(db: Session, user_id: int) -> UserNutrientsResponse:
    """
    Получить общие нутриенты из всех заказов пользователя
    """
    orders = db.query(Order).filter(Order.user_id == user_id).all()

    total_nutrients = {}

    for order in orders:
        try:
            order_nutrients = get_order_nutrients(db, order.id)

            # Суммируем нутриенты из этого заказа
            for key, nutrient in order_nutrients.total_nutrients.items():
                if key not in total_nutrients:
                    total_nutrients[key] = NutrientInfo(
                        name=nutrient.name,
                        unit_name=nutrient.unit_name,
                        amount=0,
                        daily_percentage=0
                    )
                total_nutrients[key].amount += nutrient.amount
        except HTTPException:
            continue

    # Рассчитываем проценты для общих нутриентов
    for key, nutrient in total_nutrients.items():
        nutrient_id = int(key)

        daily_norm = db.query(DailyNorm).filter(DailyNorm.nutrient_id == nutrient_id).first()
        if daily_norm and daily_norm.amount and daily_norm.amount > 0:
            daily_percentage = int(round((nutrient.amount / float(daily_norm.amount)) * 100))
            nutrient.daily_percentage = daily_percentage

    return UserNutrientsResponse(
        user_id=user_id,
        total_nutrients=total_nutrients,
        order_count=len(orders)
    )


def get_nutrients_with_translation(db: Session) -> Dict[int, Dict]:
    """Получить все нутриенты с русским переводом"""
    nutrients = db.query(Nutrient, NutrientRu).join(
        NutrientRu, Nutrient.id == NutrientRu.nutrient_id
    ).all()

    result = {}
    for nutrient, nutrient_ru in nutrients:
        result[nutrient.id] = {
            'name': nutrient_ru.name_ru,
            'name_en': nutrient.name,
            'unit_name': nutrient.unit_name
        }

    return result


@router.get("/orders/{order_id}/nutrients", response_model=OrderNutrientsResponse)
def get_order_nutrients_endpoint(order_id: int, db: Session = Depends(get_db)):
    """
    Получить нутриенты для конкретного заказа
    """
    return get_order_nutrients(db, order_id)

@router.get("/users/{user_id}/nutrients", response_model=UserNutrientsResponse)
def get_user_nutrients_endpoint(user_id: int, db: Session = Depends(get_db)):
    """
    Получить общие нутриенты из всех заказов пользователя
    """
    return get_user_total_nutrients(db, user_id)
