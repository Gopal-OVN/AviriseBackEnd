
from sqlalchemy.orm import Session
from app.models.service_type import ServiceType
from app.models.user import User

from app.schemas.service_type import CreateServiceType, UpdateServiceType
from fastapi import HTTPException


def create_service_type(db: Session, service_type: CreateServiceType, current_user: User):
    """Create a new service_type."""
    # Check if the service_type already exists based on the service_type name
    if db.query(ServiceType).filter(ServiceType.name == service_type.name).first():
        # If service_type exists, raise an error
        raise HTTPException(status_code=400, detail="ServiceType already exists")
    
    service_type_data = service_type.dict()
    service_type_data["created_by"] = current_user.user_id
    new_service_type = ServiceType(**service_type_data)
    # Create a new service_type instance with provided data
    # new_service_type = ServiceType(
    #     name=service_type.name,
    #     is_active=service_type.is_active,
    #     created_by=current_user.user_id,  # Set the user who created the role
    # )
    
    # Add the new role to the database session and commit the changes
    db.add(new_service_type)
    db.commit()
    db.refresh(new_service_type)
    
    # Return the newly created role
    return new_service_type


def get_service_type(db: Session, service_id: int):
    """Get a service_type by ID. """
    return db.query(ServiceType).filter(ServiceType.service_id ==service_id , ServiceType.is_deleted ==False).first()



# Get all serviceTypes with pagination
def get_list_service_types(db: Session, current_user: User):
    """Get all active service type."""
    # Query the database to get all service types that are not marked as deleted
    service_types = db.query(ServiceType).filter(ServiceType.is_deleted == False).order_by(ServiceType.updated_at.desc()).all()
    
    # If no service types are found, raise a 404 error
    if not service_types:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No service types found"
        )
    
    # Return the list of service types if found
    return service_types



def update_service_type(db: Session, service_id: int, service_type_data: UpdateServiceType):
    """Update an existing service type."""
    
    # Query the service type to update, ensuring it exists and isn't marked as deleted
    db_service_type = (
        db.query(ServiceType)
        .filter(ServiceType.service_id == service_id, ServiceType.is_deleted == False)
        .first()
    )
    
    if not db_service_type:
        raise HTTPException(status_code=404, detail="Service Type not found")

    # Check if the new name is unique (ignore the current record)
    existing_service_type = (
        db.query(ServiceType)
        .filter(ServiceType.name == service_type_data.name, ServiceType.service_id != service_id)
        .first()
    )
    if existing_service_type:
        raise HTTPException(
            status_code=400,
            detail=f"Service Type with name '{service_type_data.name}' already exists"
        )

    # Update fields dynamically
    update_data = service_type_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_service_type, key, value)

    # Commit and refresh
    db.commit()
    db.refresh(db_service_type)

    return db_service_type
    

  




def delete_service_type(db: Session, service_id: int):
    """Soft delete a role."""
    # Query the role to be deleted, ensuring it isn't already deleted
    service_type = db.query(ServiceType).filter(ServiceType.service_id == service_id, ServiceType.is_deleted == False).first()
    
    # If role is not found or already deleted, raise a 404 error
    if not service_type:
        raise HTTPException(status_code=404, detail="ServiceType not found or already deleted")
    
    # Mark the role as deleted and inactive
    service_type.is_deleted = True
    service_type.is_active = False
    db.commit()
    db.refresh(service_type)
    
    # Return the soft-deleted role
    return service_type