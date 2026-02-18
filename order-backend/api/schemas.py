from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from decimal import Decimal


class NutrientInfo(BaseModel):
    name: str
    unit_name: str
    amount: int
    daily_percentage: Optional[int] = None


class DishNutrientsResponse(BaseModel):
    dish_id: int
    dish_name: str
    total_weight_g: float
    nutrients: Dict[str, NutrientInfo]


class OrderNutrientsResponse(BaseModel):
    order_id: int
    total_nutrients: Dict[str, NutrientInfo]
    dishes: List[DishNutrientsResponse]


class UserNutrientsResponse(BaseModel):
    user_id: int
    total_nutrients: Dict[str, NutrientInfo]
    order_count: int


class MenuMacros(BaseModel):
    calories: int = Field(ge=0)
    protein: int = Field(ge=0)
    fat: int = Field(ge=0)
    carbs: int = Field(ge=0)


class MenuMicronutrient(BaseModel):
    name: str
    unit: str
    value: int
    coverage_percent: int


class MenuDish(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    macros: MenuMacros
    micronutrients: Dict[str, MenuMicronutrient]
    recommendations: List[str]
    score: Optional[int] = None
    image_url: Optional[str] = None


class DishResponse(BaseModel):
    id: int
    name: str
    price: float


class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    id: int
    dish_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItemCreate]


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    total_price: float
    created_at: str
    items: List[OrderItemResponse]
