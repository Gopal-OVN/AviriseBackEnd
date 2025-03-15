from pydantic import BaseModel
from datetime import datetime
from typing import Optional




class MenuGet(BaseModel):
    menu_id: Optional[int]
    menu_name: Optional[str] = None
    icon_name: Optional[str] = None
    url: Optional[str] = None
    parent_id: Optional[int] = None
    menu_order: Optional[int] = None
    child_order: Optional[int] = None
    menu_level: Optional[int] = None
    is_active: bool = True
    is_deleted: bool = False
    created_by: Optional[str] = None
    
    class Config:
    # orm_mode = True
        from_attributes = True
