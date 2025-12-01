# uvicorn admin.main:app --reload --port 8002
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from shared.models import (
    DishIngredient as DishIngredientModel,
    Dish as DishModel,
    Ingredient as IngredientModel,
    Vitamin as VitaminModel,
    Organ as OrganModel,
    DailyVitaminRequirement as DailyVitaminRequirementModel,
    VitaminOrganBenefit as VitaminOrganBenefitModel,
    IngredientVitaminContent as IngredientVitaminContentModel,
)

app = FastAPI(title="Admin Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",           # Vite dev server (если используется)
        "http://localhost:3000",           # Основной порт (если настроен nginx)
        "http://localhost:3001",           # Admin frontend
        "http://localhost:3002",           # Order frontend  
        "http://localhost:3003",           # Courier frontend
        "http://localhost:80",             # Nginx proxy (если используется)
        "http://localhost",                # Nginx без порта
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Pydantic Models ===

class DishIngredientCreate(BaseModel):
    dish_id: int
    ingredient_id: int
    amount_grams: float

class DishIngredientResponse(DishIngredientCreate):
    id: int

class DishIngredientUpdate(BaseModel):
    dish_id: Optional[int] = None
    ingredient_id: Optional[int] = None
    amount_grams: Optional[float] = None

class DishResponse(BaseModel):
    id: int
    name: str
    price: float

class IngredientResponse(BaseModel):
    id: int
    name: str

class VitaminResponse(BaseModel):
    id: int
    name: str
    short_name: str

class OrganResponse(BaseModel):
    id: int
    name: str
    description: str

class CoverageResponse(BaseModel):
    dish_name: str
    organ_name: str
    vitamin_name: str
    daily_requirement_mcg: float
    vitamin_in_dish_mcg: float
    coverage_percentage: float

# === DishIngredient CRUD ===

@app.get("/dish-ingredients/", response_model=List[DishIngredientResponse])
def get_dish_ingredients(
    dish_id: Optional[int] = None,
    ingredient_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(DishIngredientModel)
    if dish_id:
        query = query.filter(DishIngredientModel.dish_id == dish_id)
    if ingredient_id:
        query = query.filter(DishIngredientModel.ingredient_id == ingredient_id)
    return query.all()

@app.post("/dish-ingredients/", response_model=DishIngredientResponse)
def create_dish_ingredient(item: DishIngredientCreate, db: Session = Depends(get_db)):
    db_item = DishIngredientModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/dish-ingredients/{item_id}", response_model=DishIngredientResponse)
def update_dish_ingredient(
    item_id: int, item: DishIngredientUpdate, db: Session = Depends(get_db)
):
    db_item = db.query(DishIngredientModel).filter(DishIngredientModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict(exclude_unset=True).items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/dish-ingredients/{item_id}")
def delete_dish_ingredient(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(DishIngredientModel).filter(DishIngredientModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"ok": True}

# === Other Models CRUD ===

@app.get("/dishes/", response_model=List[DishResponse])
def get_dishes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    dishes = db.query(DishModel).offset(skip).limit(limit).all()
    return dishes

@app.get("/ingredients/", response_model=List[IngredientResponse])
def get_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    ingredients = db.query(IngredientModel).offset(skip).limit(limit).all()
    return ingredients

@app.get("/vitamins/", response_model=List[VitaminResponse])
def get_vitamins(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    vitamins = db.query(VitaminModel).offset(skip).limit(limit).all()
    return vitamins

@app.get("/organs/", response_model=List[OrganResponse])
def get_organs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    organs = db.query(OrganModel).offset(skip).limit(limit).all()
    return organs

# === Coverage Report API ===

from sqlalchemy import text

@app.get("/coverage-report/", response_model=List[CoverageResponse])
def get_coverage_report(
    dish_id: Optional[int] = None,
    organ_id: Optional[int] = None,
    vitamin_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    # Начальный запрос
    query = text("""
        SELECT
            d.name AS dish_name,
            o.name AS organ_name,
            v.name AS vitamin_name,
            dvr.amount AS daily_requirement_mcg,
            COALESCE(SUM(di.amount_grams / 100 * ivc.content_per_100g), 0) AS vitamin_in_dish_mcg,
            CASE
                WHEN dvr.amount > 0 THEN (SUM(di.amount_grams / 100 * ivc.content_per_100g) / dvr.amount) * 100
                ELSE 0
            END AS coverage_percentage
        FROM dishes d
        JOIN dish_ingredients di ON d.id = di.dish_id
        JOIN ingredients ing ON di.ingredient_id = ing.id
        JOIN ingredient_vitamin_contents ivc ON ing.id = ivc.ingredient_id
        JOIN vitamins v ON ivc.vitamin_id = v.id
        JOIN vitamin_organ_benefits vob ON v.id = vob.vitamin_id
        JOIN organs o ON vob.organ_id = o.id
        JOIN daily_vitamin_requirements dvr ON v.id = dvr.vitamin_id AND dvr.age_group = 'взрослый'
        WHERE 1=1
    """)

    params = {}

    if dish_id:
        query = text(str(query) + " AND d.id = :dish_id")
        params["dish_id"] = dish_id
    if organ_id:
        query = text(str(query) + " AND o.id = :organ_id")
        params["organ_id"] = organ_id
    if vitamin_id:
        query = text(str(query) + " AND v.id = :vitamin_id")
        params["vitamin_id"] = vitamin_id

    query = text(str(query) + " GROUP BY d.id, d.name, o.id, o.name, v.id, v.name, dvr.amount ORDER BY coverage_percentage DESC;")
    result = db.execute(query, params).fetchall()

    return [
        CoverageResponse(
            dish_name=row.dish_name,
            organ_name=row.organ_name,
            vitamin_name=row.vitamin_name,
            daily_requirement_mcg=row.daily_requirement_mcg,
            vitamin_in_dish_mcg=row.vitamin_in_dish_mcg,
            coverage_percentage=row.coverage_percentage
        ) for row in result
    ]



# === Health Check ===

@app.get("/health")
def health_check():
    return {"status": "ok"}
