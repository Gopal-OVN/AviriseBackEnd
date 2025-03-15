from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CreateParcelType(BaseModel):
    parcel_name : str
    description: Optional[str]
    is_active: bool = True
    
    
class GetParcelType(BaseModel):
    parcel_id: int
    parcel_name:Optional[str]
    description: Optional[str]
    is_active: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    created_by_name: Optional[str]
    created_by: int
    updated_by: Optional[int]
    
class UpdateParcelType(BaseModel):
    
    parcel_name:Optional[str]
    description: Optional[str]
    is_active: Optional[bool]
    
class DeleteResponse(BaseModel):
    message: str
    

    
class Config:
    orm_mode = True