# Courier models
from sqlalchemy import (
    Column, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, 
    Numeric, String, Text, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from shared.database import Base

class Order(Base):
   __tablename__ = "orders"
   __table_args__ = {"comment": "Заказы."}

   id = Column(Integer, primary_key=True, index=True)
   user_id = Column(Integer)
   status = Column(String, default="pending")
   total_price = Column(Numeric(precision=10, scale=2))
   created_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
   updated_at = Column(TIMESTAMP(timezone=True), onupdate=func.current_timestamp())
   items = relationship("OrderItem", back_populates="order")   
