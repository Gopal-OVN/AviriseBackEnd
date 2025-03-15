from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class IndustryType(Base):
    __tablename__ = "industry_type"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    created_by = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Reverse relationship to access companies

    companies = relationship(
        "Company", 
        back_populates="industry_type",
        overlaps="companies"
    )
    def __repr__(self):
        return f"<IndustryType(id={self.id}, name={self.name})>"
