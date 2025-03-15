from pydantic import BaseModel, Field
from typing import Optional ,List
from datetime import datetime
# from app.models.order_tracking import TrackingEnum



class GetOrderTrackingSchema(BaseModel):
    order_tracking_id: Optional[int] = None
    order_id: Optional[int] = None
    comment : Optional[str] = None
    docket: Optional[int] = None
    pod:Optional[str] = None

    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

    class Config:
        from_attributes = True


class CreateOrderTrackingSchema(BaseModel):
    order_id: Optional[int] = Field(None, description="Required when creating order tracking from API")
    is_active: Optional[bool]

    @classmethod
    def validate_order_id(cls, values):
        if not values.get("order_id"):
            raise ValueError("order_id is required when creating order tracking from API")
        return values
    
    class Config:
        orm_mode = True

class UpdateOrderTrackingSchema(BaseModel):
    # order_status: Optional[TrackingEnum]
    order_id: Optional[int]

    is_active: Optional[bool]

class DeleteOrderTrackingSchema(BaseModel):
    message : str

    

class Config:
    orm_mode = True
    