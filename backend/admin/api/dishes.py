# admin/api/dishes.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from uuid import uuid4

from shared.database import get_db
from shared.models import Dish
from shared.minio_s3 import s3, BUCKET_NAME, MINIO_ENDPOINT 

router = APIRouter(prefix="/dishes", tags=["dishes"])


class DishAdminListItem(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]
    image_url: Optional[str]

    class Config:
        from_attributes = True


class DishAdminDetail(DishAdminListItem):
    pass


class DishAdminUpdate(BaseModel):
    price: Optional[float] = Field(None, ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


@router.get("/", response_model=List[DishAdminListItem])
def list_dishes(db: Session = Depends(get_db)):
    return db.query(Dish).order_by(Dish.id).all()


@router.get("/{dish_id}", response_model=DishAdminDetail)
def get_dish_admin(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


@router.put("/{dish_id}", response_model=DishAdminDetail)
def update_dish_admin(
    dish_id: int, data: DishAdminUpdate, db: Session = Depends(get_db)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(dish, key, value)

    db.commit()
    db.refresh(dish)
    return dish

@router.post("/{dish_id}/image", response_model=DishAdminDetail)
def upload_dish_image(
    dish_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=404, detail="Dish not found")

    # расширение файла
    ext = file.filename.rsplit(".", 1)[-1].lower()
    object_name = f"{dish_id}/{uuid4().hex}.{ext}"

    # загружаем
    s3.upload_fileobj(
        Fileobj=file.file,
        Bucket=BUCKET_NAME,
        Key=object_name,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    # публичный URL (для public-read bucket)
    public_url = f"http://{MINIO_ENDPOINT}/{BUCKET_NAME}/{object_name}"
    dish.image_url = public_url
    db.commit()
    db.refresh(dish)
    return dish
