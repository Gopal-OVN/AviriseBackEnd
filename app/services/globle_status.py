from sqlalchemy.orm import Session
from app.models.globle_status import GlobleStatus
from app.schemas.globle_status import GlobleStatusCreate, GlobleStatusUpdate
from app.utils.auth import get_current_user
from fastapi import HTTPException
from app.models.user import User


# Helper function to fetch user name by user_id
def get_user_name(db: Session, user_id: int) -> str:
    """
    Fetch user's first name by user_id.
    This function queries the User model to get the user's first name using their user_id.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    return user.first_name if user else None

# Create a new GlobleStatus
def create_globle_status(db: Session, globle_status: GlobleStatusCreate, current_user: User):
    """
    Create a new GlobleStatus.
    This function adds a new GlobleStatus to the database, setting the `created_by` field to the current user.
    """
    db_globle_status = GlobleStatus(
        name=globle_status.name,
        category=globle_status.category,
        created_by=current_user.user_id,  # Set created_by as the current user
        is_active=True  # Default active status
    )
    db.add(db_globle_status)  # Add the new GlobleStatus to the session
    db.commit()  # Commit the transaction
    db.refresh(db_globle_status)  # Refresh to get the latest data (e.g., auto-generated fields)
    
    # Fetch created_by_name after commit to populate the field
    db_globle_status.created_by_name = get_user_name(db, db_globle_status.created_by)

    return db_globle_status  # Return the created GlobleStatus object

# Get all GlobleStatuses with pagination
def get_globle_statuses(db: Session, skip: int = 0, limit: int = 100):
    """
    Get all GlobleStatuses.
    This function retrieves all GlobleStatuses that are not deleted from the database.
    """
    globle_statuses = db.query(GlobleStatus).filter(GlobleStatus.is_deleted == False).offset(skip).limit(limit).all()
    
    # Populate created_by_name for each GlobleStatus
    for globle_status in globle_statuses:
        globle_status.created_by_name = get_user_name(db, globle_status.created_by)
    
    return globle_statuses  # Return the list of GlobleStatuses

# Get a specific GlobleStatus by its ID
def get_globle_status(db: Session, globle_status_id: int):
    """
    Get a GlobleStatus by ID.
    This function retrieves a GlobleStatus by its ID, ensuring it is not deleted, 
    and populates the `created_by_name` field.
    """
    db_globle_status = db.query(GlobleStatus).filter(GlobleStatus.id == globle_status_id, GlobleStatus.is_deleted == False).first()
    if db_globle_status:
        # Fetch created_by_name if the GlobleStatus exists
        db_globle_status.created_by_name = get_user_name(db, db_globle_status.created_by)
    return db_globle_status  # Return the GlobleStatus object or None if not found

# Update an existing GlobleStatus
def update_globle_status(db: Session, globle_status_id: int, globle_status_update: GlobleStatusUpdate):
    """
    Update an existing GlobleStatus.
    This function updates the details of an existing GlobleStatus in the database.
    Only the fields provided in the update schema are modified.
    """
    db_globle_status = db.query(GlobleStatus).filter(GlobleStatus.id == globle_status_id).first()
    if db_globle_status:
        # Update fields as necessary
        if globle_status_update.name:
            db_globle_status.name = globle_status_update.name
        if globle_status_update.category:
            db_globle_status.category = globle_status_update.category
        if globle_status_update.is_deleted is not None:
            db_globle_status.is_deleted = globle_status_update.is_deleted
        if globle_status_update.is_active is not None:
            db_globle_status.is_active = globle_status_update.is_active
        db.commit()  # Commit the changes to the database
        db.refresh(db_globle_status)  # Refresh to get the latest data
        return db_globle_status  # Return the updated GlobleStatus object
    return None  # Return None if the GlobleStatus was not found

# Soft delete a GlobleStatus
def soft_delete_globle_status(db: Session, globle_status_id: int):
    """
    Soft delete a GlobleStatus.
    This function marks a GlobleStatus as deleted (i.e., `is_deleted = True`) 
    without actually removing it from the database.
    """
    db_globle_status = db.query(GlobleStatus).filter(GlobleStatus.id == globle_status_id).first()
    if db_globle_status:
        db_globle_status.is_deleted = True  # Mark as deleted
        db.commit()  # Commit the change
        db.refresh(db_globle_status)  # Refresh to get the latest data
        return db_globle_status  # Return the updated object
    return None