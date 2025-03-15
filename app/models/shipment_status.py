from app.db.base import Base
from sqlalchemy import  Column, Integer, String, Boolean,DateTime ,ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class ShipmentStatusModel(Base):
    __tablename__ = 'shipment_status'

    shipment_status_id = Column(Integer, primary_key=True, index=True)
    shipment_status_name = Column(String, unique=True,nullable=False)
    description = Column(String)
    # order_id = Column(Integer, ForeignKey("order.order_id"),nullable=False)

    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)

    orders = relationship("OrderModel", back_populates="shipmentStatus")
