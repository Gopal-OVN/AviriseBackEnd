from app.db.base import Base
from sqlalchemy import  Column, Integer,Float,Enum, String, Boolean,DateTime, ForeignKey,DefaultClause
import enum
from datetime import datetime
from sqlalchemy.orm import relationship
from app.models.order import OrderModel




class OrderItemModel(Base):
    __tablename__ = "order_item"


    order_item_id = Column(Integer, primary_key=True, index=True)
    number_of_box = Column(Integer, nullable=True)
    parcel_hight = Column(Integer, nullable=True)
    parcel_width = Column(Integer, nullable=True)
    parcel_breadth = Column(Integer, nullable=True)
    volume = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)

    order_id = Column(Integer, ForeignKey("order.order_id"))



    orders = relationship("OrderModel", back_populates="orderItems")


