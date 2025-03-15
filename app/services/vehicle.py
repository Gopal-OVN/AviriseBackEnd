from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from app.models.user import User
from app.models.vehicle import VehicleModel, VehicleTypeEnum
from sqlalchemy.orm import joinedload
from app.schemas.vehicle import CreateVehicleSchema,UpdateVehicleSchema



def get_all_vehicles(db: Session, currect_user: User):

    get_vehicles_data = (
        db.query(VehicleModel).filter(VehicleModel.is_deleted==False).order_by(VehicleModel.updated_at.desc()).all()
    )

    if not get_vehicles_data:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = " No vehicle found"
        )
    
    result = []
    for vehicle in get_vehicles_data:
        result.append({
            "id" : vehicle.id,
            "name" : vehicle.name,
            "vehicle_number" : vehicle.vehicle_number,
            "insurance_validity" : vehicle.insurance_validity,
            "rc_validity" :  vehicle.rc_validity,
            "vehicle_type" : vehicle.vehicle_type.value,
            # "driver_id": vehicle.driver_id,
            # "driver_name" : vehicle.users.first_name if vehicle.users else None,
            "is_active": vehicle.is_active,
            "is_deleted": vehicle.is_deleted,
            "created_at": vehicle.created_at,
            "updated_at": vehicle.updated_at,
            "created_by": vehicle.created_by,
            "updated_by": vehicle.updated_by
        })

    return result


def get_vehicle_by_id(db: Session, id: int):
    """Get a vehicle by ID."""
    # Query the database to find the vehicle by ID, ensuring it's not marked as deleted
    get_vehicle = db.query(VehicleModel).filter(VehicleModel.id == id, VehicleModel.is_deleted == False).first()

    return get_vehicle


def create_vehicle(db: Session, vehicle_service_data: CreateVehicleSchema, current_user: User):
    """Create a new vehicle."""
    # Check if the vehicle already exists based on the vehicle name
    if db.query(VehicleModel).filter(VehicleModel.name == vehicle_service_data.name).first():
        # If vehicle exists, raise an error
        raise HTTPException(status_code=400, detail="Vehicle already exists")
    
    # Create a new vehicle instance with provided data
    new_vehicle = VehicleModel(
        name=vehicle_service_data.name,
        vehicle_number=vehicle_service_data.vehicle_number,
        insurance_validity=vehicle_service_data.insurance_validity,
        rc_validity = vehicle_service_data.rc_validity,
        vehicle_type=vehicle_service_data.vehicle_type,
        # driver_id=vehicle_service_data.driver_id,
        is_active=vehicle_service_data.is_active,
        created_by=current_user.user_id,  # Set the user who created the vehicle
    )
    
    # Add the new vehicle to the database session and commit the changes
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    
    # Return the newly created vehicle
    return new_vehicle

def update_vehicle(db: Session, id: int,vehicle_service_data : UpdateVehicleSchema):
    """
    Update an existing vehicle with the provided data.
    """
    db_vehicle = db.query(VehicleModel).filter(VehicleModel.id == id, VehicleModel.is_deleted == False).first()
    
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found ")
    


    for key, value in vehicle_service_data.dict(exclude_unset=True).items():
        if key == 'vehicle_type' and value:
            value = VehicleTypeEnum(value)  # Convert to Enum if it's a vehicle_type field
        setattr(db_vehicle, key, value)
        
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle
    # if db_vehicle:
    #     # Use vehicle.dict() to get only the fields that were updated (exclude_unset=True)
    #     for key, value in vehicle_service_data.dict(exclude_unset=True).items():
    #         setattr(db_vehicle, key, value)
    #     db.commit()  # Commit the changes
    #     db.refresh(db_vehicle)  # Refresh to reflect the updates
    #     return db_vehicle

def delete_vehicle(db: Session, id: int):
    """
    Soft delete a company by marking it as deleted (is_deleted = True).
    """

    
    db_vehicle = db.query(VehicleModel).filter(VehicleModel.id == id, VehicleModel.is_deleted == False).first()
    
    if not db_vehicle:
        raise HTTPException(status_code=404, detail="vehicle not found or already deleted")
        
    
    
    db_vehicle.is_deleted = True  # Mark as deleted (soft delete)
    db_vehicle.is_active = False
    db.commit()  # Commit the changes
    db.refresh(db_vehicle)  # Refresh to update the state
    
    return db_vehicle