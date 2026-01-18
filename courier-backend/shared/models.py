# Courier models
from sqlalchemy import (
    Column, Date, DateTime, Enum, Float, ForeignKey, Index, Integer, 
    Numeric, String, Text, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from shared.database import Base


class Courier(Base):
    __tablename__ = "couriers"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String, default="offline")  # online, delivering, offline
    current_order_id = Column(Integer, nullable=True)
    photo_url = Column(String, nullable=True) 


class Delivery(Base):
    __tablename__ = "deliveries"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    courier_id = Column(Integer, ForeignKey("couriers.id"))
    status = Column(String, default="assigned")  # assigned, picked_up, on_way, delivered
    assigned_at = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    picked_up_at = Column(TIMESTAMP(timezone=True), nullable=True)
    delivered_at = Column(TIMESTAMP(timezone=True), nullable=True)

    order = relationship("Order")
    courier = relationship("Courier")    


