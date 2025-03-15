from pydantic import BaseModel
from typing import Optional, List


# Schema for individual contact person
class ContactPerson(BaseModel):
    name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True

# Base model to handle common fields
class BranchBase(BaseModel):
    name: Optional[str] = None  # Made Optional for update
    address: Optional[str] = None
    contact_number: Optional[str] = None  # Made Optional for update
    contact_persons: Optional[List[ContactPerson]] = None  # Optional field for contact persons
    email: Optional[str] = None  # Made Optional for update
    company_id: Optional[int] = None  # Made Optional for update
    country_id: Optional[int] = None
    globle_status_id: Optional[int] = 1
    globle_status_name: Optional[str] = None  # Made Optional here
    state_id: Optional[int] = None
    city_id: Optional[int] = None
    logo: Optional[str] = None

    class Config:
        orm_mode = True

# For creating a new branch, certain fields are required
class BranchCreate(BranchBase):
    name: str
    contact_number: str
    email: str
    company_id: int
    country_id: int
    state_id: int
    city_id: int
    globle_status_id: Optional[int] = 1
    created_by: Optional[int] = None  # Optional for create (replacing created_by_id)
    updated_by: Optional[int] = None  # Optional for update (replacing updated_by_id)

# For updating a branch, all fields are optional
class BranchUpdate(BranchBase):
    is_active: Optional[bool] = True  # Still present in update schema

# Response model, includes the created and updated timestamps
class Branch(BranchBase):
    id: int
    is_active: bool = True
    is_deleted: bool = False
    globle_status_name: Optional[str] = None
    country_name: Optional[str] = None  # Add country_name field
    state_name: Optional[str] = None    # Add state_name field
    city_name: Optional[str] = None     # Add city_name field
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_by: Optional[int] = None  # Renamed to created_by
    updated_by: Optional[int] = None  # Renamed to updated_by

    class Config:
        orm_mode = True
