
from fastapi import APIRouter, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.service_type import  get_service_type, get_list_service_types, create_service_type, delete_service_type, update_service_type
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.service_type import CreateServiceType, UpdateServiceType, DeleteResponse
from app.models.service_type import ServiceType

# Initialize the API router for role-related endpoints
router = APIRouter()




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_service_type_endpoint(
    service_type: CreateServiceType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
     Endpoint to create a new service type.
    - Ensures the user is authenticated before creating.
    - Retrieves the creator’s name for response data.
    """
    try:

        # Call the `create_role` function to create the new role in the database
        new_service_type = create_service_type(
            db=db,
            service_type=service_type,
            current_user=current_user
        )
        # Get the created_by_name
        created_by_name = db.query(User).filter(User.user_id == new_service_type.created_by).first().first_name

        total = db.query(ServiceType).filter(ServiceType.is_deleted == False).count()

        # Return the newly created role with the created_by_name
        return { 
            "message": "ServiceType created successfully",
            "total": total,
            "service_type": new_service_type, 
            "created_by_name": created_by_name 
        }
    except HTTPException as e:
        # If an HTTPException occurs, raise it
        raise e



@router.get("/{service_id}", status_code=status.HTTP_200_OK)
def get_service_type_endpoint(service_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a specific service type by ID.
    - Ensures service type exists before returning details.
    - Includes created_by_name in response data.
    """
    # Query the database to find the role by ID, ensuring it's not marked as deleted
    service_type = db.query(ServiceType).filter(ServiceType.service_id == service_id, ServiceType.is_deleted == False).first()

    
    # Add the created_by_name to the response
    if service_type:
        service_type.created_by_name = db.query(User).filter(User.user_id == service_type.created_by).first().first_name

    
    service_type = get_service_type(db, service_id)
    if not service_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service Type not found")
    return {
        "message": "Service Type retrieved successfully",
        "service_type": service_type
    }
    
    
    
@router.get("/", status_code=status.HTTP_200_OK)
def get_list_service_types_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
       Retrieve all available service types.
    - Fetches all users for quick lookup.
    - Includes created_by and updated_by names in response.
    """
    
    # Fetch all users and create a dictionary for quick lookup by user_id
    all_users = db.query(User).all()
    user_dict = {user.user_id: user.first_name for user in all_users}
    
    # Query the database to get all service types that are not marked as deleted
    service_types = db.query(ServiceType).filter(ServiceType.is_deleted == False).all()
    
    # Add the created_by_name to each service type
    for service_type in service_types:
        service_type.created_by_name = user_dict.get(service_type.created_by, "Unknown")
        service_type.updated_by_name = user_dict.get(service_type.updated_by, "Unknown")
    
    try:
        # Get all service_types for the current user
        service_types = get_list_service_types(db, current_user)
    except HTTPException as e:
        # Handle exceptions and return an empty service_types list with error message
        return {
            "message": e.detail,
            "service_types": []
        }, e.status_code
    
    if not service_types:
        return {
            "message": "No service_types found in the database",
            "service_types": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "service_types retrieved successfully",
        "service_types": service_types
    }


@router.put("/{service_id}", status_code=status.HTTP_200_OK)
def update_service_type_endpoint(
    service_id: int,
    service_type_data: UpdateServiceType,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
      Update an existing service type by ID.
    - Ensures the service type exists before updating.
    - Returns the updated service type details.
    """
    # Call the `update_service_type` function to update the service type in the database
    updated_service_type = update_service_type(db, service_id, service_type_data)

    return {
        "message": "Service Type updated successfully",
        "service_type": updated_service_type
    }





@router.delete("/{service_id}",response_model=DeleteResponse )
def delete_role_endpoint(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
      Soft delete a service type by ID.
    - Marks the service type as deleted instead of removing it.
    - Returns confirmation message upon success.
    """
  
        # Attempt to delete the role
    deleted_serviceType = delete_service_type(db, service_id)
    if deleted_serviceType is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return {"message": "Service Type deeleted successfully"}
     
        
