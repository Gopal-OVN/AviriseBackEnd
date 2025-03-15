from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class City(Base):
    __tablename__ = 'city'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    state_id = Column(Integer, ForeignKey('state.id'))
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(Integer)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    state = relationship('State', back_populates='cities')
    addresses = relationship("AddressBookModel", back_populates="city")
