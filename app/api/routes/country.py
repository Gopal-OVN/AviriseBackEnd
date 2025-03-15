# app/api/routes/country.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.country import CountryCreate, CountryUpdate, PaginatedCountriesResponse, CountryResponse
from app.services.country import get_countries, create_country, get_country_by_id, update_country, delete_country
from app.db.session import get_db
from app.models.country import Country
from app.utils.auth import get_current_user

router = APIRouter()



@router.get("/", response_model=PaginatedCountriesResponse)
async def get_countries_list(
    db: Session = Depends(get_db),
    page: int = 1,
    page_size: int = 10
    ):
    """
    Fetches a paginated list of countries with is_deleted = False.
    """
    # Fetch countries with is_deleted = False
    countries = get_countries(db, page=page, page_size=page_size)
    
    # Get total count of countries where is_deleted = False
    total = db.query(Country).filter(Country.is_deleted == False).count()
    
    # Map each country to a CountryResponse
    country_responses = [CountryResponse.from_orm(country) for country in countries]
    
    return PaginatedCountriesResponse(
        total=total,
        page=page,
        page_size=page_size,
        countries=country_responses
    )


@router.post("/", response_model=CountryResponse)
async def create_country_(
    country: CountryCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
    ):
    """
    Creates a new country and returns the country details.
    """
    db_country = create_country(db, country, created_by=current_user.user_id)
    return CountryResponse.from_orm(db_country)


@router.get("/{country_id}", response_model=CountryResponse)
async def get_country_by_id(
    country_id: int,
    db: Session = Depends(get_db)
    ):
    """
    Retrieves details of a country by its ID.
    """
    db_country = get_country_by_id(db, country_id)
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return CountryResponse.from_orm(db_country)


@router.put("/{country_id}", response_model=CountryResponse)
async def update_country(
    country_id: int,
    country: CountryUpdate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
    ):
    """
    Updates an existing country and returns the updated country details.
    """
    db_country = update_country(db, country_id, country, updated_by=current_user.user_id)
    if db_country is None:
        raise HTTPException(status_code=404, detail="Country not found")
    return CountryResponse.from_orm(db_country)


@router.delete("/{country_id}", response_model=dict)
async def delete_country_route(
    country_id: int,
    db: Session = Depends(get_db)
    ):
    """
    Deletes a country by its ID (soft delete).
    """
    result = delete_country(db, country_id)
    if "message" in result:
        if result["message"] == "Country not found":
            raise HTTPException(status_code=404, detail=result["message"])
        if result["message"] == "Country already deleted":
            raise HTTPException(status_code=400, detail=result["message"])  # 400 for already deleted
        return result  # Return the message if country was deleted successfully
    raise HTTPException(status_code=400, detail="Unexpected error")  # In case of any other error


