from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GetMenuPrivilegeSchema(BaseModel):
    id: Optional[int] = None
    role_id: Optional[int] = None
    menu_id: Optional[int] = None
    menu_list: Optional[List[str]] = None
    menu_name: Optional[str] = None
    role_name: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    is_deleted: Optional[bool] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class CreateMenuPrivilegeSchema(BaseModel):
    role_ids: List[int]
    menu_ids: List[int]
    is_active: Optional[bool] = True


class UpdateMenuPrivilegeSchema(BaseModel):
    menu_ids: List[int]
    is_active: Optional[bool]

class DeleteMenuPrivilegeSchema(BaseModel):
    message : str

class Config:
    orm_mode = True
    from_attributes = True    
