from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for creating a new IndustryType
class IndustryTypeCreate(BaseModel):
    name: str  # Only name will be passed in the request body.
    is_deleted: Optional[bool] = False
    is_active: bool = True

    class Config:
        orm_mode = True
        from_attributes=True

# Schema for updating an existing IndustryType
class IndustryTypeUpdate(BaseModel):
    name: Optional[str] = None
    is_deleted: Optional[bool] = None
    is_active: Optional[bool] = None

    class Config:
        orm_mode = True
        from_attributes=True

# Response schema for IndustryType
class IndustryTypeResponse(IndustryTypeCreate):
    id: int
    created_by: int
    created_by_name: Optional[str] = None 
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes=True
