# app/services/country.py
from sqlalchemy.orm import Session
from app.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate
from app.services.common_validate_data import get_user_name


def get_countries(db: Session, page: int = 1, page_size: int = 10):
    """
    Retrieves a paginated list of countries that are not soft-deleted.
    """
    skip = (page - 1) * page_size
    # Filter out countries that are soft-deleted (is_deleted=False)
    countries = db.query(Country).filter(Country.is_deleted == False).offset(skip).limit(page_size).all()

    # Fetch created_by_name and updated_by_name for each country
    for country in countries:
        country.created_by_name = get_user_name(db, country.created_by) if country.created_by else None
        country.updated_by_name = get_user_name(db, country.updated_by) if country.updated_by else None

    return countries


def get_country_by_id(db: Session, country_id: int):
    """
    Retrieves a country by its ID and includes created_by_name and updated_by_name.
    """
    db_country = db.query(Country).filter(Country.id == country_id, Country.is_deleted == False).first()
    if db_country:
        # Fetch created_by_name and updated_by_name
        db_country.created_by_name = get_user_name(db, db_country.created_by) if db_country.created_by else None
        db_country.updated_by_name = get_user_name(db, db_country.updated_by) if db_country.updated_by else None
    return db_country


def create_country(db: Session, country: CountryCreate, created_by: int):
    """
    Creates a new country and returns the country object with created_by_name and updated_by_name.
    """
    db_country = Country(
        name=country.name,
        country_code=country.country_code,
        is_active=True,
        is_deleted=False,
        created_by=created_by,
    )
    db.add(db_country)
    db.commit()
    db.refresh(db_country)
    
    # Fetch created_by_name and updated_by_name for the created country
    db_country.created_by_name = get_user_name(db, db_country.created_by) if db_country.created_by else None
    db_country.updated_by_name = get_user_name(db, db_country.updated_by) if db_country.updated_by else None

    return db_country


def update_country(db: Session, country_id: int, country: CountryUpdate, updated_by: int):
    """
    Updates an existing country by its ID and returns the updated country.
    """
    db_country = db.query(Country).filter(Country.id == country_id, Country.is_deleted == False).first()
    if db_country:
        # Update country fields if provided
        if country.name:
            db_country.name = country.name
        if country.country_code:
            db_country.country_code = country.country_code

        db_country.updated_by = updated_by
        db.commit()
        db.refresh(db_country)

        # Fetch updated user names
        db_country.created_by_name = get_user_name(db, db_country.created_by) if db_country.created_by else None
        db_country.updated_by_name = get_user_name(db, db_country.updated_by) if db_country.updated_by else None
        return db_country
    return None


def delete_country(db: Session, country_id: int):
    """
    Soft deletes a country by its ID and returns a status message.
    """
    db_country = db.query(Country).filter(Country.id == country_id).first()
    
    if db_country:
        if db_country.is_deleted:
            return {"message": "Country already deleted"}  # Country has been soft-deleted previously
        db_country.is_deleted = True  # Soft delete
        db_country.is_active = False
        db.commit()
        db.refresh(db_country)
        return {"message": "Country successfully deleted"}
    
    return {"message": "Country not found"}  # Country doesn't exist
