from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime
from app.db.base import Base
from sqlalchemy.orm import relationship

class PermissionModel(Base):
    __tablename__ = "permission"

    permission_id = Column(Integer, primary_key=True, index=True)
    permission_name = Column(String(255), unique=True,)
    # role_id = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer)


    rolePermission = relationship("RolePermissionModel", back_populates="permission")

