from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schema for creating a new GlobleStatus
class GlobleStatusCreate(BaseModel):
    name: str
    category: str


# Schema for updating an existing GlobleStatus
class GlobleStatusUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    is_deleted: Optional[bool] = None
    is_active: Optional[bool] = None


# Response schema for GlobleStatus
class GlobleStatusResponse(GlobleStatusCreate):
    id: int
    created_by: int
    created_by_name: Optional[str] = None 
    is_deleted: Optional[bool] = False
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
