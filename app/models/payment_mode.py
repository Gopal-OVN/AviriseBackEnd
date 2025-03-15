from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
from app.models.user import User

class PaymentMode(Base):
    __tablename__ = "paymentModes"
    
    payment_id = Column(Integer, primary_key=True, index=True)
    payment_name = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer)

    orders = relationship("OrderModel", back_populates="payment_modes")

    