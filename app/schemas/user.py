from pydantic import BaseModel, EmailStr, root_validator, validator, Field
from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.branch import Branch
from app.models.company import Company


class UserOut(BaseModel):
    user_id: int
    first_name: str
    last_name: Optional[str]
    license_no: Optional[str]
    email: str
    phone_number: Optional[str]
    address: Optional[str]
    country_id: Optional[int]
    state_id: Optional[int]
    city_id: Optional[int]
    pincode: Optional[str]
    is_active: bool
    is_deleted: bool
    role_id: Optional[int]
    role_name: Optional[str]
    status_id: Optional[int] = 1
    status_name: Optional[str] = None 
    branch_id: Optional[int]
    company_id: Optional[int]
    branch_name: Optional[str]
    company_name: Optional[str]
    city_name: Optional[str]
    state_name: Optional[str]
    country_name: Optional[str]
    last_login: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    
    class Config:
        orm_mode = True  # Allows mapping ORM objects to Pydantic models
        from_attributes = True
    
    @classmethod
    def from_orm(cls, obj):
        """
        Custom method to populate the names dynamically
        """
        obj_dict = obj.__dict__.copy()  # Copy all attributes of the object

        # Add dynamic names to the response
        obj_dict['role_name'] = obj.role.role_name if obj.role else None
        obj_dict['branch_name'] = obj.branch.name if obj.branch else None
        obj_dict['company_name'] = obj.company.name if obj.company else None
        obj_dict['city_name'] = obj.city.name if obj.city else None
        obj_dict['state_name'] = obj.state.name if obj.state else None
        obj_dict['country_name'] = obj.country.name if obj.country else None
        
        return super().from_orm(obj_dict)
    
class UserCreate(BaseModel):
    first_name: str
    last_name: Optional[str]
    license_no: Optional[str]
    
    email: EmailStr
    password: Optional[str] = None  # Plain text password (will hash it before saving)
    phone_number: Optional[str]
    address: Optional[str]
    country_id: Optional[int]
    state_id: Optional[int]
    city_id: Optional[int]
    pincode: Optional[str]
    role_id: Optional[int] = None
    branch_id: Optional[int] = None
    company_id: Optional[int] = None
    status_id: Optional[int] = 1



    
    class Config:
        orm_mode = True  # Enables mapping SQLAlchemy objects to Pydantic schemas

class UserUpdate(BaseModel):
    """
    Schema for updating user details.
    All fields are optional to allow partial updates.
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: EmailStr
    phone_number: Optional[str] = None
    address: Optional[str] = None
    country_id: Optional[int] = None
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    pincode: Optional[str] = None
    status_id: Optional[int] = 1
    role_id: Optional[int] = None
    license_no: Optional[str]
    branch_id: Optional[int] = None
    company_id: Optional[int] = None
    

    class Config:
        orm_mode = True


    def __repr__(self):
        return f"UserUpdate(first_name={self.first_name}, last_name={self.last_name}, email={self.email})"

