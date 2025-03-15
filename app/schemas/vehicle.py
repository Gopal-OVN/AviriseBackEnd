from pydantic import BaseModel
from datetime import datetime,date
from typing import Optional
from app.models.vehicle import VehicleTypeEnum



class GetVehicleSchema(BaseModel):
    id : Optional[int]
    name : Optional[str]
    vehicle_number : Optional[str]
    insurance_validity : Optional[date] = None
    rc_validity : Optional[date]
    vehicle_type: Optional[VehicleTypeEnum]
    # driver_id: Optional[int]
    # driver_name : Optional[str] = None
    is_active: Optional[bool]
    is_deleted: Optional[bool]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by_name: Optional[str]
    created_by: Optional[int]
    updated_by: Optional[int]



class CreateVehicleSchema(BaseModel):
    name : str
    vehicle_number : str
    insurance_validity :date
    rc_validity : date
    vehicle_type: VehicleTypeEnum
    # driver_id : int
    is_active: bool = True

class UpdateVehicleSchema(BaseModel):
    name : Optional[str]
    vehicle_number : Optional[str]
    insurance_validity : Optional[date]
    rc_validity : Optional[date]
    vehicle_type: Optional[VehicleTypeEnum] 
    # driver_id : Optional[int]
    is_active: Optional[bool]


class DeleteVehicleschema(BaseModel):
    message : str

class Config:
    orm_mode = True

