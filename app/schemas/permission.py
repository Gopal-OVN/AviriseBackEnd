from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GetRolePermissionSchema(BaseModel):
    permission_id: Optional[int]
    # role_id: Optional[int]
    permission_name: Optional[int]
    is_active: Optional[bool]
    is_deleted: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by_name: Optional[str]
    updated_by_name: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]


class Config:
    orm_mode = True
   