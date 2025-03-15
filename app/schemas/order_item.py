from pydantic import BaseModel
from typing import Optional
# from app.models.order_item import DimentionTypeEnum
from datetime import datetime





class GetOrderItemSchema(BaseModel):
    order_item_id : Optional[int] = None
    # total_parcel_weight : Optional[int] = None
    number_of_box : Optional[int] = None
    # dimention_type : Optional[DimentionTypeEnum] = None
    # total_volume : Optional[int] = None
    parcel_hight : Optional[int] = None
    parcel_width : Optional[int] = None
    parcel_breadth : Optional[int] = None
    volume : Optional[float] = None
    # parcel_weight : Optional[int] = None
    # is_fragile : Optional[bool] = None
    is_active: Optional[bool] = None
    is_deleted: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by_name: Optional[str] = None
    updated_by_name: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    order_id: Optional[int] = None

    class Config:
        from_attributes = True


class CreateOrderItemSchmea(BaseModel):
    # total_parcel_weight : Optional[int]
    number_of_box : Optional[int]
    # dimention_type : Optional[DimentionTypeEnum]
    # total_volume : Optional[int]
    parcel_hight : Optional[int]
    parcel_width : Optional[int]
    parcel_breadth : Optional[int]
    volume : Optional[float]
    # parcel_weight : Optional[int]
    # is_fragile : Optional[bool]
    is_active: Optional[bool]
    # order_id: Optional[int]




class UpdateOrderItemSchema(BaseModel):
    # total_parcel_weight : Optional[int]
    number_of_box : Optional[int]
    # dimention_type : Optional[DimentionTypeEnum]
    # total_volume : Optional[int]
    parcel_hight : Optional[int]
    parcel_width : Optional[int]
    parcel_breadth : Optional[int]
    volume : Optional[float]
    # parcel_weight : Optional[int]
    # is_fragile : Optional[bool]
    is_active: Optional[bool]
    order_id: Optional[int]


class UpdateCreateOrderItemSchema(BaseModel):
    order_item_id: Optional[int]
    number_of_box : Optional[int]
    parcel_hight : Optional[int]
    parcel_width : Optional[int]
    parcel_breadth : Optional[int]
    volume : Optional[float]
    is_active: Optional[bool]
    order_id: Optional[int]


class DeleteOrderItemSchema(BaseModel):
    message : str

class Config:
    orm_mode = True
    from_attributes = True


