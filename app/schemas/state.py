from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class StateBase(BaseModel):
    name: str
    country_id: int
    state_code: Optional[str] = None


class StateCreate(StateBase):
    pass

class StateUpdate(StateBase):
    name: Optional[str] = None
    country_id: Optional[int] = None
    state_code: Optional[str] = None

class StateResponse(StateBase):
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
    

class PaginatedStatesResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    states: List[StateResponse]

