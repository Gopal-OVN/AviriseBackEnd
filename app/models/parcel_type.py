
from app.db.base import Base
from sqlalchemy import BigInteger, Column, Integer, String, Text, Boolean, JSON,DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship



class ParcelType(Base):
    __tablename__ = 'parcel_type'
    
    parcel_id = Column(Integer, primary_key=True,index=True)
    parcel_name = Column(String, unique=True,nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)  



    orders = relationship("OrderModel", back_populates="parcelTypes")

    