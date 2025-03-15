from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CityBase(BaseModel):
    name: str
    state_id: int
   
class CityCreate(CityBase):
    pass

class CityUpdate(CityBase):
    pass

class CityResponse(CityBase):
    id: int
    state_name: Optional[str] = None 
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

class PaginatedCityResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    cities: List[CityResponse]
