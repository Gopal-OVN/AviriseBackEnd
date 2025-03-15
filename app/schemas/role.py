from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CreateRole(BaseModel):
    role_name: str
    is_active: bool = True
    # created_by: int  

class RoleOut(BaseModel):
    role_id: int
    role_name: str
    is_active: bool
    is_deleted: bool
    created_by: int
    created_by_name: Optional[str] 
    created_at: Optional[datetime]
    updated_at: Optional[datetime]



class UpdateRole(BaseModel):
    role_name: Optional[str]
    is_active: Optional[bool]
    is_deleted: Optional[bool]


    class Config:
        orm_mode = True
