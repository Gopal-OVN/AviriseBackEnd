from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# Schema for individual contact person
class ContactPerson(BaseModel):
    name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True

class DeleteResponse(BaseModel):
    message: str

# Base schema with common fields
class CompanyBase(BaseModel):
    name: Optional[str] = None
    registration_number: Optional[str] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    industry_type_id: Optional[int] = None
    globle_status_id: Optional[int] = 1
    logo: Optional[str] = None
    address: Optional[str] = None
    contact_persons: Optional[List[ContactPerson]] = None  # Optional field for contact persons
    user_limit: Optional[int] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None


# Schema for creating a new company (fields required for creation)
class CompanyCreate(CompanyBase):
    name: str
    gst_number: str
    address: str
    registration_number: str
    industry_type_id: Optional[int] = None  # Optional field

# Schema for updating a company (all fields are optional)
class CompanyUpdate(CompanyBase):
    is_deleted: Optional[bool] = None  # Optional field for soft delete

# Response schema with additional fields like `id`, `created_at`, and `updated_at`
class Company(CompanyBase):
    id: int
    is_active: bool = True
    created_by_id: Optional[int] = None
    is_deleted: Optional[bool] = None
    created_at: datetime
    updated_at: datetime
    country_name: Optional[str] = None  # Add country_name field
    state_name: Optional[str] = None    # Add state_name field
    city_name: Optional[str] = None     # Add city_name field
    # Include names of related models
    industry_type_name: Optional[str] = None
    globle_status_name: Optional[str] = None
    created_by_name: Optional[str] = None
    

    class Config:
        orm_mode = True
        from_attributes = True 
        
