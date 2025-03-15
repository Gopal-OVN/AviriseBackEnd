# Updated Role model
from sqlalchemy import Column, Integer,BigInteger, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class MenuModel(Base):
    __tablename__ = "menu"
    menu_id = Column(BigInteger, primary_key=True, autoincrement=True)
    menu_name = Column(String(250), nullable=True)
    icon_name = Column(String(250), nullable=True)
    url = Column(String(250), nullable=True)
    parent_id = Column(BigInteger,  nullable=True)
    menu_order = Column(Integer, nullable=True)
    child_order = Column(Integer, nullable=True)
    menu_level = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(250), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(250), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)



    menuPrivilage = relationship("MenuPrivilegeModel", back_populates="menu")

