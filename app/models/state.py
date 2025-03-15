from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import backref
from app.db.base import Base

class State(Base):
    __tablename__ = "state"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    country_id = Column(Integer, ForeignKey("country.id"), nullable=False)
    state_code = Column(String(10), nullable=True, index=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    updated_by = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    
    
    country = relationship(
        "Country",
        back_populates="states",
        foreign_keys=[country_id],
        lazy="joined"
    )
    
    # Relationship with City
    cities = relationship("City", back_populates="state", lazy="joined")
    addresses = relationship("AddressBookModel", back_populates="state")


    def __repr__(self):
        return f"<State(id={self.id}, name={self.name})>"
