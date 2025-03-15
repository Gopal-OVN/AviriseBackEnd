from sqlalchemy.orm import Session
from app.models.state import State
from app.models.city import City
from app.schemas.state import StateCreate, StateUpdate, StateResponse
from app.services.common_validate_data import get_user_name
from typing import Optional

# Create a new State
def create_state(db: Session, state_create: StateCreate, created_by: int):
    """
    Create a new state and return the created state with additional user names for audit.
    """
    db_state = State(
        name=state_create.name,
        country_id=state_create.country_id,
        state_code=state_create.state_code,
        is_active=True,
        is_deleted=False,
        created_by=created_by
    )
    db.add(db_state)  # Add the new state to the session
    db.commit()  # Commit the transaction
    db.refresh(db_state)  # Refresh to get the latest data from the database

    # Fetch user names for created_by and updated_by fields
    db_state.created_by_name = get_user_name(db, db_state.created_by) if db_state.created_by else None
    db_state.updated_by_name = get_user_name(db, db_state.updated_by) if db_state.updated_by else None

    return db_state

# Update an existing State
def update_state(db: Session, state_id: int, state_update: StateUpdate, updated_by: int):
    """
    Update an existing state by ID and return the updated state with additional user names.
    """
    db_state = db.query(State).filter(State.id == state_id, State.is_deleted == False).first()
    if db_state:
        # Update fields if provided in the request
        for key, value in state_update.dict(exclude_unset=True).items():
            setattr(db_state, key, value)
        db_state.updated_by = updated_by
        db.commit()  # Commit the changes
        db.refresh(db_state)  # Refresh the object to get updated data

        # Fetch user names for created_by and updated_by fields
        db_state.created_by_name = get_user_name(db, db_state.created_by) if db_state.created_by else None
        db_state.updated_by_name = get_user_name(db, db_state.updated_by) if db_state.updated_by else None

    return db_state


# Get a single State by ID
def get_single_state(db: Session, state_id: int):
    """
    Get a single state by ID.
    """
    return db.query(State).filter(State.id == state_id).first()

# Get a list of States with optional filters for city, country, and pagination
def get_state_list(db: Session, skip: int, limit: int, city_id: Optional[int] = None, country_id: Optional[int] = None, city_name: Optional[str] = None):
    """
    Get a paginated list of states with optional filters for city, country, and city name.
    """
    # Build the query with optional filters
    query = db.query(State).filter(State.is_deleted == False)

    if city_id:
        query = query.join(City).filter(City.id == city_id)

    if country_id:
        query = query.filter(State.country_id == country_id)
    
    if city_name:
        query = query.join(City).filter(City.name.ilike(f"%{city_name}%"))

    # Fetch the states with pagination
    states = query.offset(skip).limit(limit).all()

    # Enrich states with created_by_name and updated_by_name
    for state in states:
        state.created_by_name = get_user_name(db, state.created_by) if state.created_by else None
        state.updated_by_name = get_user_name(db, state.updated_by) if state.updated_by else None
    return states



# Soft delete a State
def delete_state(db: Session, state_id: int):
    """
    Soft delete a state by ID and return a success or error message.
    """
    db_state = db.query(State).filter(State.id == state_id).first()
    if db_state:
        if db_state.is_deleted:
            return {"message": "State already deleted"}
        db_state.is_deleted = True   # Soft delete by marking is_deleted as True
        db_state.is_active = False   # Deactivate the state
        db.commit()  # Commit the changes
        db.refresh(db_state)  # Refresh the object with updated data
        return {"message": "State successfully deleted"}
    return {"message": "State not found"}  # Return error message if state not found

