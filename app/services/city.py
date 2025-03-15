from sqlalchemy.orm import Session
from app.models.city import City
from app.schemas.city import CityCreate, CityUpdate, CityResponse, PaginatedCityResponse
from app.services.common_validate_data import get_user_name
from typing import Optional
from app.models.state import State
from sqlalchemy import func


def create_city(db: Session, city: CityCreate, created_by: int):
    """
    Create a new city and return the created city with user names.
    """
    db_city = City(
        name=city.name,
        state_id=city.state_id,
        is_active=True,
        is_deleted=False,
        created_by=created_by
    )
    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    
    # Fetch user names for created and updated by fields
    db_city.created_by_name = get_user_name(db, db_city.created_by) if db_city.created_by else None
    db_city.updated_by_name = get_user_name(db, db_city.updated_by) if db_city.updated_by else None

    return db_city


def get_city(db: Session, city_id: int):
    """
    Get city by ID, return None if not found.
    """
    return db.query(City).filter(City.id == city_id).first()


async def get_city_list(db: Session, skip: int, limit: int, state_id: Optional[int], state_name: Optional[str]):
    """
    Get paginated cities with optional filters for state.
    """
    query = db.query(City).filter(City.is_deleted == False)
    
    # Apply filters for state_id and state_name if provided
    if state_id:
        query = query.filter(City.state_id == state_id)
    if state_name:
        query = query.join(State).filter(State.name.ilike(f"%{state_name}%"))
        
    total = query.count()  # Count total rows after applying filters
    cities = query.offset(skip).limit(limit).all()  # Pagination query
    
    # Enrich cities with created_by_name and updated_by_name
    for city in cities:
        city.created_by_name = get_user_name(db, city.created_by) if city.created_by else None
        city.updated_by_name = get_user_name(db, city.updated_by) if city.updated_by else None
        city.state_name = city.state.name if city.state else None
    
    return total, cities


def update_city(db: Session, city_id: int, city: CityUpdate, updated_by: int):
    """
    Update city data by ID and return the updated city.
    """
    db_city = db.query(City).filter(City.id == city_id, City.is_deleted == False).first()
    if db_city:
        for key, value in city.dict(exclude_unset=True).items():
            setattr(db_city, key, value)
        db_city.updated_by = updated_by
        db.commit()
        db.refresh(db_city)
        # Fetch user names for updated_by and created_by
        db_city.created_by_name = get_user_name(db, db_city.created_by) if db_city.created_by else None
        db_city.updated_by_name = get_user_name(db, db_city.updated_by) if db_city.updated_by else None

    return db_city


def delete_city_service(db: Session, city_id: int):
    """
    Soft delete city by ID and return success/error message.
    """
    db_city = db.query(City).filter(City.id == city_id).first()
    if db_city:
        if db_city.is_deleted:
            return {"message": "City already deleted"}
        db_city.is_deleted = True  # Soft delete the city
        db_city.is_active = False
        db.commit()
        db.refresh(db_city)
        return {"message": "City successfully deleted"}
    return {"message": "City not found"}
