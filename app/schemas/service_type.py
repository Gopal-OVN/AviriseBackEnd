from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CreateServiceType(BaseModel):
    name: str
    description: Optional[str]
    is_active: bool = True

class ServiceTypeOut(BaseModel):
    service_id: int
    name: str
    description: str
    is_active: bool
    is_deleted: bool
    created_by: int
    created_by_name: Optional[str] 
    updated_by: int
    updated_by_name: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class DeleteResponse(BaseModel):
    message: str
    
    
class UpdateServiceType(BaseModel):
    name: Optional[str]
    description: Optional[str]
    is_active: Optional[bool]



    class Config:
        orm_mode = True

