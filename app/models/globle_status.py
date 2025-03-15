from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class GlobleStatus(Base):
    __tablename__ = "globle_status"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    category = Column(String(100), nullable=False) 
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Reverse relationship to access companies
    companies = relationship("Company", backref="status_companies", foreign_keys="Company.globle_status_id")


    # Ensure unique combination of 'name' and 'category'
    __table_args__ = (
        UniqueConstraint('name', 'category', name='unique_name_category'),
    )
