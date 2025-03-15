from sqlalchemy.orm import Session
from app.models.user import User
import json
from fastapi import HTTPException,status
from app.utils.auth import get_current_user
from fastapi import Query
from typing import Optional
from app.models.parcel_type import ParcelType as ParcelModel
from app.schemas.parcel_type import CreateParcelType, GetParcelType, UpdateParcelType




def get_all_parcel_types(db: Session, current_user: User):
    """Get all active parcel_types."""
    # Query the database to get all parcel_types that are not marked as deleted
    parcel_types = db.query(ParcelModel).filter(ParcelModel.is_deleted == False).order_by(ParcelModel.updated_at.desc()).all()
    
    # If no parcel_types are found, raise a 404 error
    if not parcel_types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parcels found"
        )
    
    # Return the list of parcel_types if found
    return parcel_types


def get_parcel_type_by_id(db: Session, parcel_id: int):
    """Get a parcel_type by ID."""
    # Query the database to find the parcel_type by ID, ensuring it's not marked as deleted
    return db.query(ParcelModel).filter(ParcelModel.parcel_id == parcel_id, ParcelModel.is_deleted == False).first()


def create_parcel_type(db: Session, parcel_data_service: CreateParcelType, current_user: User):
    """Create a new parcel_type."""
    # Check if the parcel_type already exists based on the parcel_type name
    if db.query(ParcelModel).filter(ParcelModel.parcel_name == parcel_data_service.parcel_name).first():
        # If parcel_type exists, raise an error
        raise HTTPException(status_code=400, detail="Parcel type already exists")
    
    # Create a new parcel_type instance with provided data
    new_parcel_type = ParcelModel(
        parcel_name=parcel_data_service.parcel_name,
        description=parcel_data_service.description,
        is_active=parcel_data_service.is_active,
        created_by=current_user.user_id,  # Set the user who created the parcel_type
    )
    
    # Add the new parcel_type to the database session and commit the changes
    db.add(new_parcel_type)
    db.commit()
    db.refresh(new_parcel_type)
    
    # Return the newly created parcel_type
    return new_parcel_type



def update_parcel_type(db: Session, parcel_id: int,update_parcel_data_service : UpdateParcelType):
    """
    Update an existing company with the provided data.
    """
    db_parcel_type = db.query(ParcelModel).filter(ParcelModel.parcel_id == parcel_id, ParcelModel.is_deleted == False).first()
    
    if not db_parcel_type:
        raise HTTPException(status_code=404, detail="Parcel Type not found ")
        
    
    if db_parcel_type:
        # Use company.dict() to get only the fields that were updated (exclude_unset=True)
        for key, value in update_parcel_data_service.dict(exclude_unset=True).items():
            setattr(db_parcel_type, key, value)
        db.commit()  # Commit the changes
        db.refresh(db_parcel_type)  # Refresh to reflect the updates
        return db_parcel_type
    # return None
    
    
def delete_parcel_type(db: Session, parcel_id: int):
    """
    Soft delete a company by marking it as deleted (is_deleted = True).
    """

    
    db_parcel_type = db.query(ParcelModel).filter(ParcelModel.parcel_id == parcel_id, ParcelModel.is_deleted == False).first()
    
    if not db_parcel_type:
        raise HTTPException(status_code=404, detail="Parcel Type not found or already deleted")
        
    
    
    db_parcel_type.is_deleted = True  # Mark as deleted (soft delete)
    db_parcel_type.is_active = False
    db.commit()  # Commit the changes
    db.refresh(db_parcel_type)  # Refresh to update the state
    
    return db_parcel_type

