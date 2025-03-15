from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func

class DriverModel(Base):
    __tablename__ = "drivers"

    driver_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), unique=True, index=True)
    license_no = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=False)
    created_date = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    updated_date = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="drivers")
    orders = relationship("OrderModel", back_populates="drivers")
