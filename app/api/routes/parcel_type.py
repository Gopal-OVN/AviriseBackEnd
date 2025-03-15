from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional, List, Dict
from app.models.user import User
from datetime import datetime
from app.models.parcel_type import ParcelType as ParcelModel
from app.schemas.parcel_type import GetParcelType, CreateParcelType, UpdateParcelType, DeleteResponse
from app.services.parcel_type import get_all_parcel_types, get_parcel_type_by_id, create_parcel_type,update_parcel_type,delete_parcel_type


router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_parcel_types_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint to retrieve all available parcel_types.

    - **db**: Dependency to access the database session.
    - **current_user**: Dependency to get the current logged-in user.

    Returns a list of parcel_types or an appropriate message if no parcel_types are found.
    """
    
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    # Query the database to get all parcel_types that are not marked as deleted
    parcel_types = db.query(ParcelModel).filter(ParcelModel.is_deleted == False).all()

    
    # Add the created_by_name to the response
    for parcel_type in parcel_types:
        parcel_type.created_by_name = user_dict.get(parcel_type.created_by, 'Unknown')

    
    try:
        # Get all parcel_types for the current user
        parcel_types = get_all_parcel_types(db, current_user)
    except HTTPException as e:
        # Handle exceptions and return an empty parcel_types list with error message
        return {
            "message": e.detail,
            "parcel_types": []
        }, e.status_code
    
    total = db.query(ParcelModel).filter(ParcelModel.is_deleted == False).count()


    if not parcel_types:
        return {
            "message": "No parcel_types found in the database",
            "parcel_types": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "ParcelTypes retrieved successfully",
        "total": total,
        "parcel_types": parcel_types
    }


@router.get("/{parcel_id}", status_code=status.HTTP_200_OK)
def get_parcel_type_endpoint(parcel_id: int, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
   
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    # Query the database to find the parcel_type by ID, ensuring it's not marked as deleted
    parcel_type = db.query(ParcelModel).filter(ParcelModel.parcel_id == parcel_id, ParcelModel.is_deleted == False).first()

    
    
    # Add the created_by_name to the response
    if parcel_type:
        parcel_type.created_by_name = user_dict.get(parcel_type.created_by, 'Unknown')

    
    parcel_type = get_parcel_type_by_id(db, parcel_id)
    if not parcel_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ParcelModel not found")
    return {
        "message": "ParcelModel retrieved successfully",
        "parcel_type": parcel_type
    }
    
    
    
#create with json format
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_parcel_type(
    parcel:CreateParcelType,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    try:
        new_parcel_type = create_parcel_type(db=db,parcel_data_service=parcel,current_user=current_user)
        
    
    except  Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating parcel type:{str(e)}"
        )
        
    return{
        "message": "Parcel Type was create successfully",
        "created parcel": new_parcel_type
        }
        
        
# ,response_model=GetParcelType
@router.put("/{parcel_id}")
async def update_existing_parcel_type(
    parcel_id: int,
    update_parcel: UpdateParcelType,
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
        updated_parcel = update_parcel_type(db=db, parcel_id=parcel_id, update_parcel_data_service=update_parcel)
    
        # If the company is not found, raise a 404 error
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company not found : {str(e)}"
        )
    # Return the updated company data
    return{
        "message": "Parcel Type was updated successfully",
        "update parcel": updated_parcel
        } 


@router.delete("/{parcel_id}",  response_model= DeleteResponse)
def delete_parcel_type_endpoint(
    parcel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a role by ID.
    """
   
        # Attempt to delete the role
    deleted_parcel = delete_parcel_type(db, parcel_id)
    
    
    if deleted_parcel is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Parcel Type not found"
            
        )
    return {"message" : "Parcel Type deleted successfully"}
    
    
