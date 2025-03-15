from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DriverBase(BaseModel):
    user_id: int
    license_no: str
    name: str
    # vehicle_id: Optional[int] = None 
    is_active: Optional[bool] = True
    is_deleted: Optional[bool] = False
    created_by: int

class DriverCreate(BaseModel):
    user_id: int
    name : str
    license_no : str
    is_active : bool = True
    

class DriverUpdate(BaseModel):
    is_active: Optional[bool]
    is_deleted: Optional[bool]

class DriverResponse(DriverBase):
    driver_id: int
    created_date: datetime
    updated_at: datetime
    updated_date: datetime
    
    
class DeleteResponse(BaseModel):
    message: str
    


class Config:
    orm_mode = True
