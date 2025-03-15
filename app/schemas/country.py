# app/schemas/country.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CountryBase(BaseModel):
    name: str
    country_code: str

    class Config:
        orm_mode = True  # Allow Pydantic to read data from SQLAlchemy model

class CountryCreate(CountryBase):
    pass

class CountryUpdate(BaseModel):
    name: Optional[str] = None
    country_code: Optional[str] = None

class CountryResponse(CountryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_deleted: bool
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

class PaginatedCountriesResponse(BaseModel):
    total: int
    page: int
    page_size: int
    countries: List[CountryResponse]
