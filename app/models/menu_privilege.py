from sqlalchemy import Column, Integer,BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class MenuPrivilegeModel(Base):
    __tablename__ = "menu_privileges"

    id = Column(BigInteger, primary_key=True, index=True)
    role_id = Column(BigInteger, nullable=True)
    menu_id = Column(BigInteger, ForeignKey("menu.menu_id"), nullable=True )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(BigInteger, nullable=True)
    updated_by = Column(BigInteger, nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    
    
    menu = relationship("MenuModel", back_populates="menuPrivilage")
