from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.industry_type import IndustryTypeCreate, IndustryTypeUpdate, IndustryTypeResponse
from app.services.industry_type import create_industry_type, get_industry_types, get_industry_type, update_industry_type, soft_delete_industry_type
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.industry_type import  IndustryType

# Initialize the APIRouter instance for IndustryType endpoints
router = APIRouter()



# Create a new IndustryType
@router.post("/", response_model=IndustryTypeResponse)
def create_industry(industry_type: IndustryTypeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new IndustryType.
    - `industry_type`: The IndustryType data to be created.
    - `db`: The database session.
    - `current_user`: The current logged-in user (used for `created_by` field).
    """
    return create_industry_type(db=db, industry_type=industry_type, current_user=current_user)


# Get all IndustryTypes with pagination
@router.get("/", response_model=dict)
def list_industry_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get a list of all IndustryTypes with pagination.
    - `skip`: The offset (starting point) of the query.
    - `limit`: The number of items to fetch.
    """
    # Get paginated industry types and total count
    industry_types = get_industry_types(db, skip=skip, limit=limit)
    total_count = db.query(IndustryType).filter(IndustryType.is_deleted == False).count()

    return {
        "total_count": total_count,  # Total number of IndustryTypes
        "skip": skip,  # Current page (skip value)
        "limit": limit,  # Page size (limit value)
        "industry_types": industry_types,  # Paginated industry types
    }


# Get a specific IndustryType by its ID
@router.get("/{industry_type_id}", response_model=IndustryTypeResponse)
def single_industry_type(industry_type_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single IndustryType by its ID.
    - `industry_type_id`: The ID of the IndustryType to retrieve.
    """
    db_industry_type = get_industry_type(db, industry_type_id)
    if db_industry_type is None:
        # If the IndustryType doesn't exist, return 404 error
        raise HTTPException(status_code=404, detail="IndustryType not found")
    return db_industry_type


# Update an existing IndustryType by its ID
@router.put("/{industry_type_id}", response_model=IndustryTypeResponse)
def update_industry(industry_type_id: int, industry_type_update: IndustryTypeUpdate, db: Session = Depends(get_db)):
    """
    Update an IndustryType by its ID.
    - `industry_type_id`: The ID of the IndustryType to be updated.
    - `industry_type_update`: The fields to update in the IndustryType.
    """
    db_industry_type = update_industry_type(db, industry_type_id, industry_type_update)
    if db_industry_type is None:
        # If the IndustryType doesn't exist, return 404 error
        raise HTTPException(status_code=404, detail="IndustryType not found")
    return db_industry_type


# Soft delete an IndustryType by its ID
@router.delete("/{industry_type_id}", response_model=IndustryTypeResponse)
def soft_delete_industry(industry_type_id: int, db: Session = Depends(get_db)):
    """
    Soft delete an IndustryType by its ID.
    - `industry_type_id`: The ID of the IndustryType to be deleted.
    """
    db_industry_type = soft_delete_industry_type(db, industry_type_id)
    if db_industry_type is None:
        # If the IndustryType doesn't exist, return 404 error
        raise HTTPException(status_code=404, detail="IndustryType not found")
    return db_industry_type


