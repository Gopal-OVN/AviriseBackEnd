from sqlalchemy import Column, Integer, String, Boolean, DateTime , ForeignKey
from datetime import datetime
from app.db.base import Base
from sqlalchemy.orm import relationship


class RolePermissionModel(Base):
    __tablename__ = "role_permission"

    role_permission_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer,ForeignKey("roles.role_id") ,nullable=True)
    permission_id = Column(Integer, ForeignKey("permission.permission_id"), nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer)

    role = relationship("Role", back_populates="rolePermission")
    permission = relationship("PermissionModel", back_populates="rolePermission")

