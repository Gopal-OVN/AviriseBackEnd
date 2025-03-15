from sqlalchemy.orm import Session
from app.models.company import Company as CompanyModel
from app.schemas.company import CompanyCreate, CompanyUpdate, DeleteResponse
from typing import Optional
from sqlalchemy.orm import joinedload
from app.utils.auth import get_current_user
from app.models.user import User
import json
from fastapi import HTTPException
from app.models.globle_status import GlobleStatus
from app.models.industry_type import IndustryType
from fastapi import Query
from sqlalchemy import or_, and_



# CRUD function to create a new company
def create_company(db: Session, company: CompanyCreate, current_user: User):
    """
    Create a new company after validating the GST and PAN numbers.
    Automatically sets the `created_by_id` field.
    """
    # Validate the gst_number and pan_number length
    if len(company.gst_number) > 15:
        raise ValueError("GST Number must be at most 15 characters")
    if company.pan_number and len(company.pan_number) > 10:
        raise ValueError("PAN Number must be at most 10 characters")
    
    # Handling `contact_persons`
    if company.contact_persons == "":
        company.contact_persons = None  # Set to None if empty string

    # Only parse if `contact_persons` is a string
    if isinstance(company.contact_persons, str):
        try:
            company.contact_persons = json.loads(company.contact_persons)  # Parse as JSON
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON format for contact_persons"
            )
    elif company.contact_persons is None:
        company.contact_persons = []  # Default to an empty list if not provided
    # If it's already a list, we just use it as is

    # Set the `globle_status_id` to 1 by default if not provided
    if not company.globle_status_id:
        company.globle_status_id = 1

    # Create a new company and associate the created_by_id
    db_company = CompanyModel(**company.dict())
    db_company.created_by_id = current_user.user_id 
    db.add(db_company)  # Add the company to the session
    db.commit()  # Commit the transaction
    db.refresh(db_company)  # Refresh to retrieve database-generated values
    # Fetch created_by_name and updated_by_name for the created country
    db_compnay.created_by_name = get_user_name(db, db_compnay.created_by) if db_compnay.created_by else None
    return db_company


# CRUD function to get a company by ID
def get_company(db: Session, company_id: int):
    """
    Retrieve a company by its ID, ensuring it's not marked as deleted.
    """
    return (
        db.query(CompanyModel)
        .options(joinedload(CompanyModel.industry_type), joinedload(CompanyModel.globle_status))
        .filter(CompanyModel.id == company_id, CompanyModel.is_deleted == False)
        .first()
    )


def get_companies(
    db: Session,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    industry_type_name: Optional[str] = None,
    globle_status_name: Optional[str] = None,
    state_id: Optional[int] = None,
    city_id: Optional[int] = None
    ):
    """
    Retrieve companies with pagination and search filters.
    """
    # Calculate skip and limit based on page and page_size
    skip = (page - 1) * page_size
    limit = page_size

    query = db.query(CompanyModel).filter(CompanyModel.is_deleted == False)

    # Apply search filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                CompanyModel.name.ilike(search_term),
                CompanyModel.address.ilike(search_term)
            )
        )
    # Apply filters for related fields
    if industry_type_name:
        query = query.join(CompanyModel.industry_type).filter(IndustryType.name.ilike(f"%{industry_type_name}%"))
    
    if globle_status_name:
        query = query.join(CompanyModel.globle_status).filter(GlobleStatus.name.ilike(f"%{globle_status_name}%"))
    
    if state_id:
        query = query.filter(CompanyModel.state_id == state_id)
    if city_id:
        query = query.filter(CompanyModel.city_id == city_id)
    
    # Get the total count of companies
    total_count = query.count()
    
    # Apply pagination
    companies = query.offset(skip).limit(limit).all()

    return companies, total_count


# CRUD function to update an existing company
def update_company(db: Session, company_id: int, company: CompanyUpdate):
    """
    Update an existing company with the provided data.
    """
    db_company = db.query(CompanyModel).filter(CompanyModel.id == company_id, CompanyModel.is_deleted == False).first()
    if db_company:
        # Use company.dict() to get only the fields that were updated (exclude_unset=True)
        for key, value in company.dict(exclude_unset=True).items():
            setattr(db_company, key, value)
        db.commit()  # Commit the changes
        db.refresh(db_company)  # Refresh to reflect the updates
        return db_company
    return None  # Return None if the company is not found


# CRUD function to soft delete a company
def delete_company(db: Session, company_id: int):
    """
    Soft delete a company by marking it as deleted (is_deleted = True).
    """
    db_company = db.query(CompanyModel).filter(CompanyModel.id == company_id, CompanyModel.is_deleted == False).first()
    if db_company:
        db_company.is_deleted = True  # Mark as deleted (soft delete)
        db_company.is_active = False
        db.commit()  # Commit the changes
        db.refresh(db_company)  # Refresh to update the state
        return db_company
    return None  # Return None if the company is not found
