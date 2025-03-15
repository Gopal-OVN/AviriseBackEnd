from pydantic import BaseModel
from typing import Optional ,List
from datetime import datetime
from app.models.order import PaymentTypeEnum ,DimensionTypeEnum
from app.schemas.order_item import CreateOrderItemSchmea,GetOrderItemSchema,UpdateCreateOrderItemSchema
from app.schemas.address_book import GetAddressBookSchema,CreateAddressBookSchema
from app.schemas.order_tracking import CreateOrderTrackingSchema, GetOrderTrackingSchema


class GetOrderSchema(BaseModel):
    order_id: Optional[int]
    docket_no: Optional[int]
    manual_docket: Optional[str]
    payment_type: Optional[PaymentTypeEnum]
    cod_amount: Optional[int]
    service_type_id: Optional[int]
    service_type_name: Optional[str] = None

    payment_mode_id: Optional[int]
    payment_mode_name: Optional[str] = None

    customer_id: Optional[int]
    customer_name: Optional[str] = None

    gst_number: Optional[int]
    # address_book_id: Optional[int]
    receiver_address_book_id: Optional[int]
    sender_address_book_id: Optional[int]

    # receiver_address_book: Optional[str] = None
    # sender_address_book : Optional[str] = None

    receiver_company_name: Optional[str] = None
    sender_company_name : Optional[str] = None

    parcel_type_id: Optional[int]
    parcel_type_name: Optional[str] = None

    shipment_status_id:Optional[int]
    shipment_status_name:Optional[str]=None

    driver_id:Optional[int]
    driver_name:Optional[str] = None

    vehicle_id:Optional[int]
    vehicle_name:Optional[str] = None
    
    comment:Optional[str] = None
    appointment_date_time: Optional[datetime] = None
    shipment_value: Optional[int]
    invoice_no: Optional[int]
    e_way_bill: Optional[int]
    forwarding: Optional[int]
    booking_instruction: Optional[str]
    is_active: Optional[bool]
    is_deleted: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by_name: Optional[str]
    updated_by_name: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]
    order_items: Optional[List[GetOrderItemSchema]]
    # address_books: Optional[List[GetAddressBookSchema]]
    receiver_address: Optional[GetAddressBookSchema]
    sender_address: Optional[GetAddressBookSchema]
    order_trackings:Optional[GetOrderTrackingSchema]


    total_box_size : Optional[int]
    total_no_of_box: Optional[int]
    dimension_type : Optional[DimensionTypeEnum]
    total_volume : Optional[float]
    parcel_weight : Optional[int]
    is_fragile : Optional[bool]
    is_docket_auto: Optional[bool]
    pod:Optional[str]
    display_docket: Optional[str]





class CreateOrderSchema(BaseModel):
    docket_no: Optional[int]
    manual_docket: Optional[str]
    payment_type: Optional[PaymentTypeEnum]
    cod_amount: Optional[int]
    service_type_id: Optional[int]
    payment_mode_id: Optional[int]
    customer_id: Optional[int]
    gst_number: Optional[int]
    # address_book_id: Optional[int]
    receiver_address_book_id: Optional[int] = 0
    sender_address_book_id: Optional[int] = 0

    parcel_type_id: Optional[int]

    shipment_status_id:Optional[int] =1
    # appointment_date_time: Optional[datetime] = None
    shipment_value: Optional[int]
    invoice_no: Optional[int]
    e_way_bill: Optional[int]
    forwarding: Optional[int]
    booking_instruction: Optional[str]
    is_active: Optional[bool]

    order_items: Optional[List[CreateOrderItemSchmea]] # List of order items
    receiver_address: Optional[CreateAddressBookSchema]
    sender_address: Optional[CreateAddressBookSchema]
    order_trackings:Optional[CreateOrderTrackingSchema]


    total_box_size : Optional[int]
    total_no_of_box: Optional[int]
    dimension_type : Optional[DimensionTypeEnum]
    total_volume : Optional[float]
    parcel_weight : Optional[int]
    is_fragile : Optional[bool] = False
    is_docket_auto: Optional[bool] = False





class UpdateOrderSchema(BaseModel):
    # order_item_id: Optional[int]
    payment_type: Optional[PaymentTypeEnum]
    cod_amount: Optional[int]
    service_type_id: Optional[int]
    payment_mode_id: Optional[int]
    customer_id: Optional[int]
    gst_number: Optional[int]
    # address_book_id: Optional[int]
    receiver_address_book_id: Optional[int]
    sender_address_book_id: Optional[int]

    # appointment_date_time: Optional[datetime] = None
    comment:Optional[str] = None
    parcel_type_id: Optional[int]
    shipment_status_id:Optional[int]
    shipment_value: Optional[int]
    invoice_no: Optional[int]
    e_way_bill: Optional[int]
    forwarding: Optional[int]
    booking_instruction: Optional[str]
    is_active: Optional[bool]
    order_items: Optional[List[UpdateCreateOrderItemSchema]]  # List of order items
    receiver_address: Optional[CreateAddressBookSchema]
    sender_address: Optional[CreateAddressBookSchema]
    order_trackings:Optional[CreateOrderTrackingSchema]



    total_box_size : Optional[int]
    total_no_of_box: Optional[int]
    dimension_type : Optional[DimensionTypeEnum]
    total_volume : Optional[float]
    parcel_weight : Optional[int]
    is_fragile : Optional[bool]
    is_docket_auto: Optional[bool]


class AssignDriverVehicleSchema(BaseModel):
    driver_id: int
    vehicle_id: int
    appointment_date_time: Optional[datetime] = None
    order_trackings:Optional[CreateOrderTrackingSchema]


class UpdateShipmentStatusSchema(BaseModel):
    # order_id: int
    shipment_status_id:Optional[int]
    comment:Optional[str] = None
    order_trackings:Optional[CreateOrderTrackingSchema]

class DeleteOrderSchema(BaseModel):
    message : str

class Config:
    orm_mode = True
    from_attributes = True




