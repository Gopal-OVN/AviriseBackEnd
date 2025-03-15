from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.globle_status import GlobleStatusCreate, GlobleStatusUpdate, GlobleStatusResponse
from app.services.globle_status import create_globle_status, get_globle_statuses, get_globle_status, update_globle_status, soft_delete_globle_status
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.globle_status import GlobleStatus

# Initialize the APIRouter instance for GlobleStatus endpoints
router = APIRouter()



# Create a new GlobleStatus
@router.post("/", response_model=GlobleStatusResponse)
def create_globle(globle_status: GlobleStatusCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new GlobleStatus.
    - `globle_status`: The GlobleStatus data to be created.
    - `db`: The database session.
    - `current_user`: The current logged-in user (used for `created_by` field).
    """
    return create_globle_status(db=db, globle_status=globle_status, current_user=current_user)


# Get all GlobleStatuses with pagination
@router.get("/", response_model=dict)
def list_globle_statuses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of all GlobleStatuses with pagination.
    - `skip`: The offset (starting point) of the query.
    - `limit`: The number of items to fetch.
    """
    # Get paginated globle statuses and total count
    globle_statuses = db.query(GlobleStatus).filter(GlobleStatus.is_deleted == False).offset(skip).limit(limit).all()
    total_count = db.query(GlobleStatus).filter(GlobleStatus.is_deleted == False).count()

    return {
        "total_count": total_count,
        "skip": skip,
        "limit": limit,
        "globle_statuses": [GlobleStatusResponse.from_orm(gs) for gs in globle_statuses],  # Convert to Pydantic schema
    }


# Get a specific GlobleStatus by its ID
@router.get("/{globle_status_id}", response_model=GlobleStatusResponse)
def single_globle_status(globle_status_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single GlobleStatus by its ID.
    - `globle_status_id`: The ID of the GlobleStatus to retrieve.
    """
    db_globle_status = get_globle_status(db, globle_status_id)
    if db_globle_status is None:
        # If the GlobleStatus doesn't exist, return 404 error
        raise HTTPException(status_code=404, detail="GlobleStatus not found")
    return db_globle_status


# Update an existing GlobleStatus by its ID
@router.put("/{globle_status_id}", response_model=GlobleStatusResponse)
def update_globle(globle_status_id: int, globle_status_update: GlobleStatusUpdate, db: Session = Depends(get_db)):
    """
    Update an existing GlobleStatus by its ID.
    - `globle_status_id`: The ID of the GlobleStatus to be updated.
    - `globle_status_update`: The fields to update in the GlobleStatus.
    """
    db_globle_status = update_globle_status(db, globle_status_id, globle_status_update)
    if db_globle_status is None:
        # If the GlobleStatus doesn't exist, return 404 error
        raise HTTPException(status_code=404, detail="GlobleStatus not found")
    return db_globle_status


# Soft delete a GlobleStatus by its ID
@router.delete("/{globle_status_id}")
def soft_delete_globle(globle_status_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a GlobleStatus by its ID.
    - `globle_status_id`: The ID of the GlobleStatus to be deleted.
    """
    db_globle_status = soft_delete_globle_status(db, globle_status_id)
    # Already deleted message
    if db_globle_status.is_deleted:
        return {"message": "Globle Status is already deleted."}
    
    if db_globle_status is None:
        raise HTTPException(status_code=404, detail="GlobleStatus not found")
    return {"message": "Globle Status successfully deleted."}

