from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional, List, Dict
from datetime import datetime
from app.models.user import User
from app.models.vehicle import VehicleModel, VehicleTypeEnum    
from app.services.vehicle import get_all_vehicles,get_vehicle_by_id,create_vehicle,update_vehicle,delete_vehicle
from app.schemas.vehicle import CreateVehicleSchema,UpdateVehicleSchema,DeleteVehicleschema




router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_vehicles_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
   
    # get all user
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    vehicles = get_all_vehicles(db, current_user)

    # Query the database to get all vehicles that are not marked as deleted

    
    # Add the created_by_name to the response // who is created
   

    for vehicle in vehicles:
        vehicle['created_by_name'] = user_dict.get(vehicle['created_by'], 'Unknown')


    total = db.query(VehicleModel).filter(VehicleModel.is_deleted == False).count()

    if not vehicles:
        return {
            "message": "No vehicles found in the database",
            "vehicles": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "Vehicle retrieved successfully",
        "total": total,
        "vehicles": vehicles
    }

# @router.get("/{id}", status_code=status.HTTP_200_OK)
# def get_vehicle_endpoint(id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
   
#     all_users = db.query(User).all()
#     user_dict = {user.user_id: user.first_name for user in all_users}
#     # Query the database to find the vehicle by ID, ensuring it's not marked as deleted
#     vehicle = db.query(VehicleModel).filter(VehicleModel.id == id, VehicleModel.is_deleted == False).first()

    
    
#     # Add the created_by_name to the response
#     if vehicle:
#         vehicle.created_by_name = user_dict.get(vehicle.created_by, 'Unknown')

    
#     vehicle = get_vehicle_by_id(db, id)
#     if not vehicle:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
#     return {
#         "message": "Vehicle retrieved successfully",
#         "vehicles": vehicle
#     }

@router.get("/{id}", status_code=status.HTTP_200_OK)
def get_vehicle_endpoint(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    
    vehicle = get_vehicle_by_id(db, id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    vehicle.created_by_name = user_dict.get(vehicle.created_by, 'Unknown')
    return {
        "message": "Vehicle retrieved successfully",
        "vehicle": vehicle
    }



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_vehicle(
    vehicle:CreateVehicleSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    try:
        new_vehicle = create_vehicle(db=db,vehicle_service_data=vehicle,current_user=current_user)
        
    
    except  Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating vehicle :{str(e)}"
        )
        
    return{
        "message": "Vehicle was create successfully",
        "vehicles": new_vehicle
        }


@router.put("/{id}")
async def update_existing_vehicle(
    id: int,
    vehicle: UpdateVehicleSchema,
    db: Session = Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
    """
    Endpoint to update an existing company.

    Updates the company data in the database using the provided company ID
    and the new data. Returns the updated company details if found. 
    Otherwise, returns a 404 error if the company does not exist.
    """
    # Update the company data in the database using the provided company ID
    try: 
        updated_vehicle = update_vehicle(db=db, id=id, vehicle_service_data=vehicle)
    
        # If the company is not found, raise a 404 error
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle not found : {str(e)}"
        )
    # Return the updated company data
    return{
        "message": "Vehicle was updated successfully",
        "vehicles": updated_vehicle
        } 

@router.delete("/{id}",  response_model= DeleteVehicleschema)
def delete_vehicle_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a role by ID.
    """
   
        # Attempt to delete the role
    deleted_vehicle = delete_vehicle(db, id)
    
    
    if deleted_vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
            
        )
    return {"message" : "Vehicle deleted successfully",}


