from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.state import StateCreate, StateUpdate, StateResponse, PaginatedStatesResponse
from app.db.session import get_db
from app.models.state import State
from app.services.state import create_state, get_single_state, get_state_list, update_state, delete_state
from app.models.user import User
from app.models.city import City
from app.utils.auth import get_current_user
from typing import Optional



router = APIRouter()



@router.get("/{state_id}", response_model=StateResponse)
def read_state(state_id: int, db: Session = Depends(get_db)):
    """
    Get a state by its ID.
    
    This route retrieves a state using its ID. If the state is not found, 
    it raises a 404 HTTP exception.
    
    Returns the state's details as a response.
    """
    db_state = get_single_state(db=db, state_id=state_id)
    if db_state is None:
        raise HTTPException(status_code=404, detail="State not found")
    return db_state


@router.post("/", response_model=StateResponse)
def create_state_route(state_create: StateCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Create a new state.
    
    This route takes the state creation data (StateCreate schema) and the authenticated user's ID,
    then creates a new state record in the database.
    
    Returns the created state's data as a response.
    """
    return create_state(db=db, state_create=state_create, created_by=current_user.user_id)


@router.put("/{state_id}", response_model=StateResponse)
def update_state_route(state_id: int, state_update: StateUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a state's data by its ID.
    
    This route updates an existing state's data using the provided state ID and new data. 
    The `updated_by` field is also updated with the current user's ID.
    
    If the state is not found, it raises a 404 error. Otherwise, it returns the updated state's details.
    """
    db_state = update_state(db=db, state_id=state_id, state_update=state_update, updated_by=current_user.user_id)
    if db_state is None:
        raise HTTPException(status_code=404, detail="State not found")
    return db_state


@router.get("/", response_model=PaginatedStatesResponse)
async def get_states(
    page: int = 1, 
    page_size: int = 100, 
    city_id: Optional[int] = None, 
    city_name: Optional[str] = None, 
    country_id: Optional[int] = None, 
    db: Session = Depends(get_db)
    ):
    """
    Get a paginated list of states with optional filters for city and country.
    
    This route retrieves a list of states with pagination and filtering options. 
    You can filter by city ID, city name, or country ID. The `page` and `page_size` 
    parameters control pagination.
    
    Returns a paginated list of states along with total count, total pages, and current page.
    """
    # Validate page and page_size parameters to prevent invalid values
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Invalid page or page_size.")
    
    skip = (page - 1) * page_size
    limit = page_size

    # Get states with applied filters
    states = get_state_list(db, skip, limit, city_id=city_id, country_id=country_id, city_name=city_name)
    
    total = db.query(State).filter(State.is_deleted == False).count()
    
    # Return the paginated list of states with additional metadata
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "states": states,
    }


@router.delete("/{state_id}", response_model=dict)
async def delete_state_route(state_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a state by its ID.
    
    This route marks the state as deleted without removing it from the database permanently.
    It checks if the state exists, and if not, returns a 404 error.
    
    Returns a success message if the state was successfully deleted or a 400 error for unexpected issues.
    """
    result = delete_state(db, state_id)
    if "message" in result:
        if result["message"] == "State not found":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    raise HTTPException(status_code=400, detail="Unexpected error")

