from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CreatePaymentMode(BaseModel):
    payment_name : str
    description : str
    is_active : bool = True
    
    
class PaymentModeOut(BaseModel):
    payment_id : int
    payment_name : str
    description : str
    is_active : bool
    is_deleted : bool
    created_by : int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by : int
    
class UpdatePaymentModeSchema(BaseModel): 
    payment_name : Optional[str]
    description: Optional[str]
    is_active : Optional[bool]

class DeleteResponse(BaseModel):
    message: str
    

class Config: 
    orm_mode = True

    
    
