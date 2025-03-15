from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.city import CityResponse, CityCreate, CityUpdate, PaginatedCityResponse
from app.services.city import create_city, get_city, get_city_list, update_city, delete_city_service
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional, List, Dict
from app.models.user import User
from app.models.city import City
from app.models.state import State

router = APIRouter()

@router.post("/", response_model=CityResponse)
def create_city_route(
    city: CityCreate, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(get_current_user)
    ):
    """
    Create a new city.
    
    Takes city creation data and the authenticated user, then creates a new city entry in the database.
    Returns the created city details as a response.
    """
    return create_city(db=db, city=city, created_by=current_user.user_id)


@router.get("/", response_model=PaginatedCityResponse)
async def get_city_list_route(
    page: int = 1, 
    page_size: int = 50, 
    state_id: Optional[int] = None, 
    state_name: Optional[str] = None, 
    db: Session = Depends(get_db)
    ):
    """
    Get a list of cities with pagination and filters.
    
    Allows pagination with page and page_size parameters, and optional filtering by state_id or state_name.
    Returns paginated city data along with total count and total pages.
    """
    # Validate page and page_size parameters
    if page < 1 or page_size < 1 or page_size > 100:
        raise HTTPException(status_code=400, detail="Invalid page or page_size.")
    skip = (page - 1) * page_size
    limit = page_size
    # Fetch cities with pagination and optional filtering
    total, cities = await get_city_list(db, skip, limit, state_id, state_name)
    # Return paginated city data
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "cities": cities,
    }


@router.get("/{city_id}", response_model=CityResponse)
def get_city_route(city_id: int, db: Session = Depends(get_db)):
    """
    Get a city by ID.
    
    Fetches and returns the city data for a given city ID.
    If the city is not found, a 404 error is raised.
    """
    db_city = get_city(db=db, city_id=city_id)
    if not db_city:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@router.put("/{city_id}", response_model=CityResponse)
def update_existing_city(city_id: int, city: CityUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Update a city's data.
    
    Takes city update data and updates an existing city entry in the database. 
    If the city is not found, a 404 error is raised.
    Returns the updated city details.
    """
    db_city = update_city(db=db, city_id=city_id, city=city, updated_by=current_user.user_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city


@router.delete("/{city_id}", response_model=dict)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    """
    Soft delete a city by ID.
    
    Marks a city as deleted in the database. If the city cannot be found, a 404 error is raised.
    If any unexpected errors occur, a 400 error is returned.
    """
    result = delete_city_service(db, city_id)
    if "message" in result:
        if result["message"] == "State not found":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    raise HTTPException(status_code=400, detail="Unexpected error")


