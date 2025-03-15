from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional, List, Dict
from app.models.user import User
from datetime import datetime
from app.models.shipment_status import ShipmentStatusModel
from app.services.shipment_status import get_all_shipment_status,get_shipment_status_by_id,create_shipment_status,update_shipment_status,delete_shipment_status
from app.schemas.shipment_status import CreateShipmentStatusSchema, UpdateShipmentStatusSchema,DeleteResponse


router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_shipment_status_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint to retrieve all available shipment_status.

    - **db**: Dependency to access the database session.
    - **current_user**: Dependency to get the current logged-in user.

    Returns a list of shipment_status or an appropriate message if no shipment_status are found.
    """
    
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    # Query the database to get all shipment_status that are not marked as deleted
    shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.is_deleted == False).all()

    
    # Add the created_by_name to the response
    for shipment_status in shipment_status:
        shipment_status.created_by_name = user_dict.get(shipment_status.created_by, 'Unknown')

    
    try:
        # Get all shipment_status for the current user
        shipment_status = get_all_shipment_status(db, current_user)
    except HTTPException as e:
        # Handle exceptions and return an empty shipment_status list with error message
        return {
            "message": e.detail,
            "shipment_status": []
        }, e.status_code
    
    total = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.is_deleted == False).count()


    if not shipment_status:
        return {
            "message": "No shipment status found in the database",
            "shipment_status": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "Shipment status retrieved successfully",
        "total": total,
        "shipment_status": shipment_status
    }

@router.get("/{shipment_status_id}", status_code=status.HTTP_200_OK)
def get_shipment_status(shipment_status_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
   
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    # Query the database to find the shipment_status by ID, ensuring it's not marked as deleted
    shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.shipment_status_id == shipment_status_id, ShipmentStatusModel.is_deleted == False).first()

    
    
    # Add the created_by_name to the response
    if shipment_status:
        shipment_status.created_by_name = user_dict.get(shipment_status.created_by, 'Unknown')

    
    shipment_status = get_shipment_status_by_id(db, shipment_status_id)
    if not shipment_status:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shipment Status not found")
    return {
        "message": "Shipment Status retrieved successfully",
        "shipment_status": shipment_status
    }



#create with json format
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_shipmentStatus_endpoint(
    shipmentStatus:CreateShipmentStatusSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    # try:
        new_shipmentStatus = create_shipment_status(db=db,create_shipment_service_data=shipmentStatus,current_user=current_user)
        
        return new_shipmentStatus
    
    # except  Exception as e:
    #     raise HTTPException(
    #         status_code=400,
    #         detail=f"Error creating shipment status:{str(e)}"
    #     )
        
    # return{
    #     "message": "Shipment status was create successfully",
    #     "created parcel": new_shipment_status
    #     }
    


@router.put("/{shipment_status_id}")
async def update_existing_shipment_status(
    shipment_status_id: int,
    update_shipmentStatus: UpdateShipmentStatusSchema,
    db: Session = Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
    
    # Update the company data in the database using the provided company ID
    # try: 
        updated_shipmentStatus = update_shipment_status(db=db, shipment_status_id=shipment_status_id, update_shipment_status_service_data=update_shipmentStatus, current_user=current_user)
    
        return updated_shipmentStatus
        # If the company is not found, raise a 404 error
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=f"Company not found : {str(e)}"
    #     )
    # # Return the updated company data
    # return{
    #     "message": "Shipment Status was updated successfully",
    #     "update data": updated_shipmentStatus
    #     } 


@router.delete("/{shipment_status_id}",  response_model= DeleteResponse)
def delete_shipment_status_endpoint(
    shipment_status_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a shipment status by ID.
    """
   
        # Attempt to delete the role
    deleted_parcel = delete_shipment_status(db, shipment_status_id)
    
    
    if deleted_parcel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment status not found"
            
        )
    return {"message" : "Shipment status deleted successfully"}

