from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class GetAddressBookSchema(BaseModel):
    address_book_id : Optional[int]
    # customer_id : Optional[int]
    # user_name: Optional[str] = None

    # name : Optional[str]
    company_name : Optional[str]
    contact_name : Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    
    
    address : Optional[str]

    country_id: Optional[int]
    country_name: Optional[str] = None
    state_id : Optional[int]
    state_name: Optional[str] = None
    city_id : Optional[int] 
    city_name: Optional[str] = None   
    pincode  : Optional[str]
    is_active: Optional[bool]
    is_deleted: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by_name: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    is_manual_generate: Optional[bool]



class CreateAddressBookSchema(BaseModel):
    # customer_id:int
    # name:Optional[str]
    company_name:Optional[str]
    contact_name:Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    
    
    address: Optional[str]
    country_id: Optional[int] = 1
    state_id: Optional[int]
    city_id: Optional[int]
    pincode: Optional[str]
    is_active:Optional[bool] = True
    is_manual_generate: Optional[bool] = False



class UpdateAddressBookSchema(BaseModel):
    # customer_id :  int
    # name : Optional[str]
    company_name:Optional[str]
    contact_name:Optional[str]
    email: Optional[str]
    phone_number: Optional[str]
    address : Optional[str]
    country_id: Optional[int]
    state_id : Optional[int]
    city_id : Optional[int]    
    pincode  : Optional[str]
    is_active: Optional[bool]
    is_manual_generate: Optional[bool]



class DeleteAddressBookSchema(BaseModel):
    message: str

class Config:
    orm_mode = True