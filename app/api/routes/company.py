from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.schemas.company import CompanyCreate, CompanyUpdate, Company, DeleteResponse
from app.services.company import create_company, get_company, get_companies, update_company, delete_company
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.forms.company_forms import create_new_company_form, update_company_form
from typing import Optional, List, Dict
from app.models.company import Company as CompanyModel  


router = APIRouter()




# Endpoint to create a new company (as JSON)
@router.post("/", response_model=Company)
async def create_new_company(
    company: CompanyCreate,  # Expecting the data in the request body as JSON
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
    ):
    """
    Endpoint to create a new company.

    Validates the JSON data and creates a new company in the database,
    associating the current authenticated user as the creator of the company.
    Returns the created company details.
    """
    try:
        # Call the function to create a new company in the database
        new_company = create_company(db, company, current_user=current_user.user_id)
        return new_company
    except Exception as e:
        # If an error occurs, raise a 400 HTTP error with the error message
        raise HTTPException(
            status_code=400,
            detail=f"Error creating company: {str(e)}"
        )


@router.get("/{company_id}", response_model=Company)
async def get_existing_company(company_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a single company by its ID.

    Fetches the company data from the database using the provided company ID.
    Returns the company details if found. Otherwise, returns a 404 error.
    """
    company = get_company(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Populate industry_type_name and globle_status_name
    company_dict = company.__dict__
    company_dict["industry_type_name"] = company.industry_type.name if company.industry_type else None
    company_dict["globle_status_name"] = company.globle_status.name if company.globle_status else None
    return company_dict


@router.get("/", response_model=dict)
async def get_list_companies(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    industry_type_name: Optional[str] = None,
    globle_status_name: Optional[str] = None,
    state_id: Optional[int] = None,
    city_id: Optional[int] = None,
    db: Session = Depends(get_db)
    ):
    """
    Endpoint to retrieve a list of companies with pagination and filters.
    """
    # Retrieve companies based on filters
    companies, total_companies = get_companies(
        db,
        page=page,  # Pass page and page_size directly
        page_size=page_size,  # Pass page_size directly
        search=search,
        industry_type_name=industry_type_name,
        globle_status_name=globle_status_name,
        state_id=state_id,
        city_id=city_id
    )
    
    # Add industry_type_name and globle_status_name to response
    for company in companies:
        company.industry_type_name = company.industry_type.name if company.industry_type else None
        company.globle_status_name = company.globle_status.name if company.globle_status else None

    # Format the response with pagination details
    response = {
        "total": total_companies,
        "page": page,
        "page_size": page_size,
        "companies": [
            Company.from_orm(company).dict()  # Use Pydantic model here for serialization
            for company in companies
        ],
    }
    
    return response


@router.put("/{company_id}", response_model=Company)
async def update_existing_company(
    company_id: int,
    company: CompanyUpdate,
    db: Session = Depends(get_db)
    ):
    """
    Endpoint to update an existing company.

    Updates the company data in the database using the provided company ID
    and the new data. Returns the updated company details if found. 
    Otherwise, returns a 404 error if the company does not exist.
    """
    # Update the company data in the database using the provided company ID
    updated_company = update_company(db, company_id, company)
    if updated_company is None:
        # If the company is not found, raise a 404 error
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    # Return the updated company data
    return updated_company


@router.delete("/{company_id}", response_model=DeleteResponse)
async def soft_delete_company(
    company_id: int,
    db: Session = Depends(get_db)
    ):
    """
    Endpoint to soft delete a company by its ID.
    """
    deleted_company = delete_company(db, company_id)
    if deleted_company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return {"message": "Company deleted successfully"}

