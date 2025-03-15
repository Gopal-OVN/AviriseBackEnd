from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GetShipmentStatusSchema(BaseModel):
    shipment_status_id: int
    shipment_status_name:Optional[str]
    description: Optional[str]
    is_active: Optional[bool]
    is_deleted: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by_name: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]


class CreateShipmentStatusSchema(BaseModel):
    shipment_status_name : str
    description: Optional[str]
    is_active: bool = True

class UpdateShipmentStatusSchema(BaseModel):
    
    shipment_status_name:Optional[str]
    description: Optional[str]
    is_active: Optional[bool]
    
class DeleteResponse(BaseModel):
    message: str
    

    
class Config:
    orm_mode = True




