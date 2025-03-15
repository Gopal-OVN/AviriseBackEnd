from sqlalchemy.orm import Session
from app.models.industry_type import IndustryType
from app.schemas.industry_type import IndustryTypeCreate, IndustryTypeUpdate, IndustryTypeResponse
from app.utils.auth import get_current_user
from fastapi import Depends
from app.models.user import User
from app.services.common_validate_data import get_user_name



# Create IndustryType
def create_industry_type(db: Session, industry_type: IndustryTypeCreate, current_user: User = Depends(get_current_user)):
    """
    Create a new industry type and return the created industry type.
    """
    # Create a new IndustryType object
    db_industry_type = IndustryType(
        name=industry_type.name,
        created_by=current_user.user_id,
        is_deleted=industry_type.is_deleted,
        is_active=industry_type.is_active
    )
    db.add(db_industry_type) # Add the new IndustryType to the session
    db.commit() # Commit the transaction
    db.refresh(db_industry_type) # Refresh to get the latest data from the database

    # Populate 'created_by_name' by fetching user name
    db_industry_type.created_by_name = get_user_name(db, db_industry_type.created_by)

    # Return the IndustryTypeResponse model
    return IndustryTypeResponse.from_orm(db_industry_type)

# Get all IndustryTypes with created_by_name
def get_industry_types(db: Session, skip: int = 0, limit: int = 100):
    """
    Get a paginated list of all industry types, including the 'created_by_name' field.
    """
    industry_types = db.query(IndustryType).filter(IndustryType.is_deleted == False).offset(skip).limit(limit).all()

    # Populate created_by_name for each IndustryType
    for industry_type in industry_types:
        industry_type.created_by_name = get_user_name(db, industry_type.created_by)

    # Return the list of IndustryTypes as IndustryTypeResponse
    return [IndustryTypeResponse.from_orm(industry_type) for industry_type in industry_types]

# Get a single IndustryType by ID
def get_industry_type(db: Session, industry_type_id: int):
    """
    Get a single industry type by ID and return it with 'created_by_name'.
    """
    db_industry_type = db.query(IndustryType).filter(IndustryType.id == industry_type_id, IndustryType.is_deleted == False).first()
    if db_industry_type:
        # Fetch and assign 'created_by_name'
        db_industry_type.created_by_name = get_user_name(db, db_industry_type.created_by)
        return IndustryTypeResponse.from_orm(db_industry_type)
    return None  # Return None if IndustryType is not found

# Update IndustryType
def update_industry_type(db: Session, industry_type_id: int, industry_type_update: IndustryTypeUpdate):
    """
    Update an existing industry type by ID and return the updated industry type.
    """
    db_industry_type = db.query(IndustryType).filter(IndustryType.id == industry_type_id).first()
    if db_industry_type:
        # Update fields only if new values are provided
        if industry_type_update.name:
            db_industry_type.name = industry_type_update.name
        if industry_type_update.is_deleted is not None:
            db_industry_type.is_deleted = industry_type_update.is_deleted
        if industry_type_update.is_active is not None:
            db_industry_type.is_active = industry_type_update.is_active
        db.commit()  # Commit the changes
        db.refresh(db_industry_type)  # Refresh the object with the updated data

        # Populate created_by_name after the update
        db_industry_type.created_by_name = get_user_name(db, db_industry_type.created_by)

        # Return the updated IndustryType as IndustryTypeResponse
        return IndustryTypeResponse.from_orm(db_industry_type)
    return None  # Return None if IndustryType is not found

# Soft delete IndustryType
def soft_delete_industry_type(db: Session, industry_type_id: int):
    """
    Soft delete an industry type by ID and return a success or error message.
    """
    db_industry_type = db.query(IndustryType).filter(IndustryType.id == industry_type_id).first()
    if db_industry_type:
        # Mark the industry type as deleted
        db_industry_type.is_deleted = True
        db.commit()  # Commit the changes
        db.refresh(db_industry_type)  # Refresh the object with the updated data
        return {"message": "Industry Type successfully deleted."}
    return {"message": "Industry Type not found."}  # Return error message if not found
