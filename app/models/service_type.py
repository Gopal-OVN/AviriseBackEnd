# Updated Role model
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.order import OrderModel

class ServiceType(Base):
    __tablename__ = "service_type"

    service_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    description = Column(String(1000))
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    orders = relationship("OrderModel", back_populates="serviceTypes")

