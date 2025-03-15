from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List

class GetRolePermissionSchema(BaseModel):
    role_permission_id: Optional[int] = None
    role_id: Optional[int] = None
    permission_id: Optional[int] = None
    permission_name: Optional[str] = None
    role_name: Optional[str] = None

    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True
   

class CreateRolePermissionSchema(BaseModel):
    role_ids: List[int]
    permission_ids: List[int]
    is_active: Optional[bool] = True

class UpdateRolePermissionSchema(BaseModel):
    # role_id: Optional[int]
    permission_ids: List[int]
    is_active: Optional[bool]

class DeleteRolePermissionSchema(BaseModel):
    message : str

class Config:
    orm_mode = True

