from datetime import datetime
from app.db.base import Base
from sqlalchemy import  Column, Integer,Enum, String, Boolean,DateTime, ForeignKey,DefaultClause
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func





class OrderTrackingModel(Base):
    __tablename__ = "order_tracking"

    order_tracking_id = Column(Integer,primary_key=True,index=True)
    order_id = Column(Integer, ForeignKey("order.order_id"),nullable=True)
   

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)


    orders = relationship("OrderModel", back_populates="orderTrackings")

    