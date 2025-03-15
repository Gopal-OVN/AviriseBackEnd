from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Country(Base):
    __tablename__ = "country"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    country_code = Column(String(10), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    # Relationship with State
    states = relationship("State", back_populates="country", lazy="joined")
    addresses = relationship("AddressBookModel", back_populates="countries")


