# uvicorn admin.main:app --reload --port 8002
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from shared.database import get_db
from sqlalchemy.sql import func
from shared.models import (
    DishIngredient as DishIngredientModel,
    Dish as DishModel,
    Ingredient as IngredientModel,
    Organ as OrganModel,
    Nutrient as NutrientModel,
    IngredientNutrientContent as INC,
)

# --- MinIO клиент ---
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

MINIO_ENDPOINT = "http://s3.healthy.local"  # ← для Minikube
MINIO_ACCESS_KEY = "minioadmin" # FIX 
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET = "healthy-menu-dishes"

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='us-east-1'
)

# --- Fast Api ---
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


class NutrientResponse(BaseModel):
    """Нутриент: витамин или минерал."""
    id: int
    name: str
    short_name: str
    type: str
    unit: str

class NutrientContentCreate(BaseModel):
    ingredient_id: int
    nutrient_id: int
    content_per_100g: float

class NutrientContentResponse(NutrientContentCreate):
    id: int
    ingredient_name: str
    nutrient_name: str

class OrganResponse(BaseModel):
    id: int
    name: str
    description: str


class CoverageResponse(BaseModel):
    """Покрытие суточной нормы нутриентов по органам для блюда."""
    dish_name: str
    organ_name: str
    nutrient_name: str
    daily_requirement_amount: float
    daily_requirement_unit: str
    nutrient_in_dish_amount: float
    nutrient_in_dish_unit: str
    coverage_percentage: float

class PresignRequest(BaseModel):
    dish_id: int
    filename: str  

class DishCreate(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None


class DishUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)  # ≥ 0
    description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        # Разрешить входные данные как dict, и конвертировать числа
        populate_by_name = True
        extra = "forbid"  # запретить неизвестные поля (защита от id!)


class DishFullResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str] = None
    image_url: Optional[str] = None

class DishIngredientBatchUpdate(BaseModel):
    updates: List[DishIngredientUpdate]
    deletions: List[int] = []

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
    return db.query(DishModel).offset(skip).limit(limit).all()


@app.get("/ingredients/", response_model=List[IngredientResponse])
def get_ingredients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(IngredientModel).offset(skip).limit(limit).all()


@app.get("/nutrients/", response_model=List[NutrientResponse])
def get_nutrients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    nutrients = db.query(NutrientModel).offset(skip).limit(limit).all()
    return nutrients


@app.get("/organs/", response_model=List[OrganResponse])
def get_organs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(OrganModel).offset(skip).limit(limit).all()

# === Dish CRUD ===

@app.post("/dishes/", response_model=DishFullResponse)
def create_dish(dish: DishCreate, db: Session = Depends(get_db)):
    db_dish = DishModel(**dish.dict())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@app.get("/dishes/{dish_id}", response_model=DishFullResponse)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@app.put("/dishes/{dish_id}", response_model=DishFullResponse)
def update_dish(dish_id: int, dish_update: DishUpdate, db: Session = Depends(get_db)):
    print("➡️ dish_id:", dish_id)
    print("➡️ dish_update:", dish_update.dict(exclude_unset=True))
    print("➡️ raw data:", dish_update)
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    
    for key, value in dish_update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_dish, key, value)
    
    db.commit()
    db.refresh(db_dish)
    return db_dish


@app.delete("/dishes/{dish_id}")
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    db_dish = db.query(DishModel).filter(DishModel.id == dish_id).first()
    if not db_dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    db.delete(db_dish)
    db.commit()
    return {"ok": True}

# === Coverage Report API ===

from sqlalchemy import text

@app.get("/coverage-report/", response_model=List[CoverageResponse])
def get_coverage_report(
    dish_id: Optional[int] = None,
    organ_id: Optional[int] = None,
    nutrient_id: Optional[int] = None,
    db: Session = Depends(get_db)
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


@app.post("/presign-upload/")
async def presign_upload(req: PresignRequest):
    """Генерирует временный URL для загрузки изображения"""
    try:
        # Формат ключа: dishes/{dish_id}/original.jpg
        key = f"dishes/{req.dish_id}/original.{req.filename.split('.')[-1].lower()}"

        # Генерируем presigned URL (действителен 15 минут)
        url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': MINIO_BUCKET,
                'Key': key,
                'ContentType': 'image/jpeg',  # можно уточнить по расширению
            },
            ExpiresIn=900,  # 15 минут
            HttpMethod='PUT'
        )

        # Публичный URL для отображения
        public_url = f"{MINIO_ENDPOINT}/{MINIO_BUCKET}/{key}"

        return {
            "upload_url": url,
            "public_url": public_url,
            "key": key
        }
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dish-ingredients/enhanced/")
def get_dish_ingredients_enhanced(
    dish_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Возвращает состав блюда с названиями вместо ID"""
    query = db.query(
        DishIngredientModel.id,
        DishIngredientModel.dish_id,
        DishModel.name.label('dish_name'),
        DishIngredientModel.ingredient_id,
        IngredientModel.name.label('ingredient_name'),
        DishIngredientModel.amount_grams
    ).join(
        DishModel, DishIngredientModel.dish_id == DishModel.id
    ).join(
        IngredientModel, DishIngredientModel.ingredient_id == IngredientModel.id
    )
    
    if dish_id:
        query = query.filter(DishIngredientModel.dish_id == dish_id)
    
    return [
        {
            "id": row.id,
            "dish_id": row.dish_id,
            "dish_name": row.dish_name,
            "ingredient_id": row.ingredient_id,
            "ingredient_name": row.ingredient_name,
            "amount_grams": row.amount_grams
        }
        for row in query.all()
    ]

from sqlalchemy import func

@app.get("/dish-ingredients/stats/")
def get_dish_ingredients_stats(db: Session = Depends(get_db)):
    """Статистика по составу блюд"""
    total = db.query(DishIngredientModel).count()
    dishes_count = db.query(func.count(func.distinct(DishIngredientModel.dish_id))).scalar()
    ingredients_count = db.query(func.count(func.distinct(DishIngredientModel.ingredient_id))).scalar()
    
    # Топ блюд по количеству ингредиентов
    top_dishes_query = db.query(
        DishModel.name,
        func.count(DishIngredientModel.id).label('ingredient_count')
    ).join(DishIngredientModel, DishModel.id == DishIngredientModel.dish_id)\
     .group_by(DishModel.id, DishModel.name)\
     .order_by(func.count(DishIngredientModel.id).desc())\
     .limit(5).all()
    
    top_dishes = [{"name": row[0], "count": row[1]} for row in top_dishes_query]
    
    return {
        "total_entries": total,
        "unique_dishes": dishes_count,
        "unique_ingredients": ingredients_count,
        "top_dishes": top_dishes
    }


@app.get("/dish-ingredients/enhanced/")
def get_dish_ingredients_enhanced(
    dish_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Возвращает состав блюда с названиями вместо ID"""
    from sqlalchemy.orm import joinedload
    
    query = db.query(
        DishIngredientModel.id,
        DishIngredientModel.dish_id,
        DishModel.name.label('dish_name'),
        DishIngredientModel.ingredient_id,
        IngredientModel.name.label('ingredient_name'),
        DishIngredientModel.amount_grams
    ).join(
        DishModel, DishIngredientModel.dish_id == DishModel.id
    ).join(
        IngredientModel, DishIngredientModel.ingredient_id == IngredientModel.id
    )
    
    if dish_id:
        query = query.filter(DishIngredientModel.dish_id == dish_id)
    
    results = query.all()
    
    # Преобразуем в словари
    return [
        {
            "id": row.id,
            "dish_id": row.dish_id,
            "dish_name": row.dish_name,
            "ingredient_id": row.ingredient_id,
            "ingredient_name": row.ingredient_name,
            "amount_grams": row.amount_grams
        }
        for row in results
    ]


@app.put("/dish-ingredients/batch/")
def update_dish_ingredients_batch(
    batch: DishIngredientBatchUpdate,
    db: Session = Depends(get_db)
):
    """Обновление нескольких записей состава блюда"""
    results = []
    
    # Обновления
    for update_data in batch.updates:
        if update_data.id:
            item = db.query(DishIngredientModel).filter(DishIngredientModel.id == update_data.id).first()
            if item:
                for key, value in update_data.dict(exclude_unset=True, exclude={'id'}).items():
                    if value is not None:
                        setattr(item, key, value)
                results.append({"id": item.id, "action": "updated"})
    
    # Удаления
    for item_id in batch.deletions:
        item = db.query(DishIngredientModel).filter(DishIngredientModel.id == item_id).first()
        if item:
            db.delete(item)
            results.append({"id": item_id, "action": "deleted"})
    
    db.commit()
    return {"results": results}

# === NutrientContent CRUD ===

@app.get("/nutrient-contents/", response_model=List[NutrientContentResponse])
def get_contents(db: Session = Depends(get_db)):
    return db.query(
            INC.id,
            INC.ingredient_id,
            INC.nutrient_id,
            INC.content_per_100g,
            IngredientModel.name.label('ingredient_name'),
            NutrientModel.name.label('nutrient_name')
        ).join(IngredientModel).join(NutrientModel).all()

@app.post("/nutrient-contents/", response_model=NutrientContentResponse)
def create_content(body: NutrientContentCreate, db: Session = Depends(get_db)):
    row = INC(**body.dict())
    db.add(row); db.commit(); db.refresh(row)
    return db.query(...).filter(INC.id==row.id).join(...).one() # тот же запрос


# ------------------------------------------------------------------
#  INGREDIENTS  CRUD
# ------------------------------------------------------------------
class IngredientCreate(BaseModel):
    name: str

class IngredientUpdate(BaseModel):
    name: Optional[str] = None

@app.post("/ingredients/", response_model=IngredientResponse)
def create_ingredient(body: IngredientCreate, db: Session = Depends(get_db)):
    row = IngredientModel(**body.dict())
    db.add(row); db.commit(); db.refresh(row)
    return row

@app.put("/ingredients/{ing_id}", response_model=IngredientResponse)
def update_ingredient(ing_id: int, body: IngredientUpdate, db: Session = Depends(get_db)):
    row = db.query(IngredientModel).filter(IngredientModel.id == ing_id).first()
    if not row: raise HTTPException(404, "Ingredient not found")
    if body.name is not None: row.name = body.name
    db.commit(); db.refresh(row)
    return row

@app.delete("/ingredients/{ing_id}")
def delete_ingredient(ing_id: int, db: Session = Depends(get_db)):
    row = db.query(IngredientModel).filter(IngredientModel.id == ing_id).first()
    if not row: raise HTTPException(404, "Ingredient not found")
    db.delete(row); db.commit()
    return {"ok": True}


# ------------------------------------------------------------------
#  NUTRIENTS  CRUD
# ------------------------------------------------------------------
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

@app.post("/nutrients/", response_model=NutrientResponse)
def create_nutrient(body: NutrientCreate, db: Session = Depends(get_db)):
    row = NutrientModel(**body.dict())
    db.add(row); db.commit(); db.refresh(row)
    return row

@app.put("/nutrients/{nut_id}", response_model=NutrientResponse)
def update_nutrient(nut_id: int, body: NutrientUpdate, db: Session = Depends(get_db)):
    row = db.query(NutrientModel).filter(NutrientModel.id == nut_id).first()
    if not row: raise HTTPException(404, "Nutrient not found")
    for k,v in body.dict(exclude_unset=True).items(): setattr(row,k,v)
    db.commit(); db.refresh(row)
    return row

@app.delete("/nutrients/{nut_id}")
def delete_nutrient(nut_id: int, db: Session = Depends(get_db)):
    row = db.query(NutrientModel).filter(NutrientModel.id == nut_id).first()
    if not row: raise HTTPException(404, "Nutrient not found")
    db.delete(row); db.commit()
    return {"ok": True}


# ------------------------------------------------------------------
#  INGREDIENT-NUTRIENT-CONTENTS  CRUD
# ------------------------------------------------------------------
from shared.models import IngredientNutrientContent as INC   # добавьте в импорт выше

class NutrientContentCreate(BaseModel):
    ingredient_id: int
    nutrient_id: int
    content_per_100g: float

class NutrientContentUpdate(BaseModel):
    ingredient_id: Optional[int] = None
    nutrient_id: Optional[int] = None
    content_per_100g: Optional[float] = None

@app.post("/nutrient-contents/", response_model=NutrientContentResponse)
def create_nutrient_content(body: NutrientContentCreate, db: Session = Depends(get_db)):
    row = INC(**body.dict())
    db.add(row); db.commit(); db.refresh(row)
    return db.query(
            INC.id,
            INC.ingredient_id,
            INC.nutrient_id,
            INC.content_per_100g,
            IngredientModel.name.label('ingredient_name'),
            NutrientModel.name.label('nutrient_name')
        ).join(IngredientModel).join(NutrientModel).filter(INC.id == row.id).first()

@app.put("/nutrient-contents/{cid}", response_model=NutrientContentResponse)
def update_nutrient_content(cid: int, body: NutrientContentUpdate, db: Session = Depends(get_db)):
    row = db.query(INC).filter(INC.id == cid).first()
    if not row: raise HTTPException(404, "Content row not found")
    for k,v in body.dict(exclude_unset=True).items(): setattr(row,k,v)
    db.commit(); db.refresh(row)
    return db.query(...).filter(INC.id == cid).join(...).first()   # тот же запрос

@app.delete("/nutrient-contents/{cid}")
def delete_nutrient_content(cid: int, db: Session = Depends(get_db)):
    row = db.query(INC).filter(INC.id == cid).first()
    if not row: raise HTTPException(404, "Content row not found")
    db.delete(row); db.commit()
    return {"ok": True}

# === Health Check ===

@app.get("/health")
def health_check():
    return {"status": "ok"}
