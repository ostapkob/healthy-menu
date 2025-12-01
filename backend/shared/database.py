import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  # ← добавь
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/food_db"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()  # ← добавь это

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
