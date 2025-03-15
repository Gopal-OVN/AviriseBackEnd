from sqlalchemy.orm import Session
from app.models.user import User
import json
from fastapi import HTTPException,status
from app.utils.auth import get_current_user
from fastapi import Query
from typing import Optional
from app.models.shipment_status import ShipmentStatusModel
from app.schemas.shipment_status import CreateShipmentStatusSchema, UpdateShipmentStatusSchema


def get_all_shipment_status(db: Session, current_user: User):
    """Get all active shipment_status."""
    # Query the database to get all shipment_status that are not marked as deleted
    shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.is_deleted == False).all()
    # .order_by(ShipmentStatusModel.updated_at.desc())
    # If no shipment_status are found, raise a 404 error
    if not shipment_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No shiment status found"
        )
    
    # Return the list of shipment_status if found
    return shipment_status

def get_shipment_status_by_id(db: Session, shipment_status_id: int):
    """Get a shipment_status by ID."""
    # Query the database to find the shipment_status by ID, ensuring it's not marked as deleted
    get_data_by_id = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.shipment_status_id == shipment_status_id, ShipmentStatusModel.is_deleted == False).first()

    return get_data_by_id

def create_shipment_status(db: Session, create_shipment_service_data: CreateShipmentStatusSchema, current_user: User):
    """Create a new shipment_status."""
    # Check if the shipment_status already exists based on the shipment_status name
    
    try:
        if db.query(ShipmentStatusModel).filter(ShipmentStatusModel.shipment_status_name == create_shipment_service_data.shipment_status_name).first():
            # If shipment_status exists, raise an error
            raise HTTPException(status_code=400, detail="Shipment status already exists")
        
        # Create a new shipment_status instance with provided data

        shipment_status_dict = create_shipment_service_data.dict(exclude_unset=True)
        shipment_status_dict["created_by"] = current_user.user_id
        new_shipment_status = ShipmentStatusModel(**shipment_status_dict)
        # new_shipment_status = ShipmentStatusModel(
        #     name=create_shipment_service_data.name,
        #     description=create_shipment_service_data.description,
        #     is_active=create_shipment_service_data.is_active,
        #     created_by=current_user.user_id,  # Set the user who created the shipment_status
        # )
        
        # Add the new shipment_status to the database session and commit the changes
        db.add(new_shipment_status)
        db.commit()
        db.refresh(new_shipment_status)
        
        # Return the newly created shipment_status
        return {
            "message": "Shipment status created successfully",
            "shipment_status": new_shipment_status
        } 
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating shipment status: {str(e)}")


def update_shipment_status(db: Session, shipment_status_id: int,update_shipment_status_service_data : UpdateShipmentStatusSchema, current_user: User):
    """
    Update an existing company with the provided data.
    """
    try:
        db_shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.shipment_status_id == shipment_status_id, ShipmentStatusModel.is_deleted == False).first()
        
        if not db_shipment_status:
            raise HTTPException(status_code=404, detail="Shipment Status not found ")
            
        
        # if db_shipment_status:
        #     # Use company.dict() to get only the fields that were updated (exclude_unset=True)
        #     for key, value in update_shipment_status_service_data.dict(exclude_unset=True).items():
        #         setattr(db_shipment_status, key, value)

        update_data = update_shipment_status_service_data.dict(exclude_unset=True)
        update_data["updated_by"] = current_user.user_id

        for key, value in update_data.items():
            setattr(db_shipment_status, key, value)


        db.commit()  # Commit the changes
        db.refresh(db_shipment_status)  # Refresh to reflect the updates
            
        return {
            "message": "Shipment status updated successfully",
            "shipment_status": db_shipment_status
            } 


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Error updating shipmnt status: {str(e)}")

def delete_shipment_status(db: Session, shipment_status_id: int):
    """
    Soft delete a company by marking it as deleted (is_deleted = True).
    """

    
    db_shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.shipment_status_id == shipment_status_id, ShipmentStatusModel.is_deleted == False).first()
    
    if not db_shipment_status:
        raise HTTPException(status_code=404, detail="Shipment Status not found or already deleted")
        
    
    
    db_shipment_status.is_deleted = True  # Mark as deleted (soft delete)
    db_shipment_status.is_active = False
    db.commit()  # Commit the changes
    db.refresh(db_shipment_status)  # Refresh to update the state
    
    return db_shipment_status


