from fastapi import Form, Depends, HTTPException
from typing import Optional
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.models.company import Company
import json


# Form handler to create a new company
async def create_new_company_form(
    name: str = Form(...),
    registration_number: str = Form(...),
    gst_number: str = Form(...),
    address: str = Form(...),
    logo: Optional[str] = Form(None),
    contact_persons: Optional[str] = Form(None),  # Form as string (JSON string expected)
    user_limit: Optional[int] = Form(None),
    country_id: Optional[int] = Form(None),
    state_id: Optional[int] = Form(None),
    city_id: Optional[int] = Form(None),
    industry_type_id: Optional[int] = Form(None),  # Handle as integer (None if not provided)
    globle_status_id: int = Form(1),  # Default value set to 1
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    try:
        # Ensure industry_type_id is None if not provided or if input is an empty string
        if industry_type_id == "":
            industry_type_id = None  # Set to None if empty string is passed
        
        # Convert industry_type_id to integer if it's not None
        if industry_type_id is not None:
            try:
                industry_type_id = int(industry_type_id)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="industry_type_id must be a valid integer"
                )

        # If contact_persons is passed as an empty string, set it to None
        if contact_persons == "":
            contact_persons = None

        # If contact_persons is passed, parse it as JSON
        if contact_persons:
            try:
                contact_persons = json.loads(contact_persons)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON format for contact_persons"
                )
        else:
            contact_persons = []  # Default to an empty list if not provided

        # Create the CompanyCreate Pydantic model from the form data
        company = CompanyCreate(
            name=name,
            registration_number=registration_number,
            gst_number=gst_number,
            address=address,
            logo=logo,
            contact_persons=contact_persons,  # Now it's a Python list or dict
            user_limit=user_limit,
            country_id=country_id,
            state_id=state_id,
            city_id=city_id,
            industry_type_id=industry_type_id,  # Pass to the model
            globle_status_id=globle_status_id,  # Pass to the model
        )

        return company

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating company form: {str(e)}"
        )



# Form handler to update an existing company
async def update_company_form(
    company_id: int,
    name: Optional[str] = Form(None), 
    registration_number: Optional[str] = Form(None), 
    gst_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    logo: Optional[str] = Form(None),
    contact_persons: Optional[str] = Form(None),  # Form as string (JSON string expected)
    user_limit: Optional[int] = Form(None),
    country_id: Optional[int] = Form(None),
    state_id: Optional[int] = Form(None),
    city_id: Optional[int] = Form(None),
    is_deleted: Optional[bool] = Form(None),
    industry_type_id: Optional[int] = Form(None),  # Optional field for update
    globle_status_id: Optional[int] = Form(None),  # Optional field for update
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    try:
        # Find the company by ID
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Create a CompanyUpdate instance from the form data
        updated_company = CompanyUpdate(
            name=name if name else company.name,
            registration_number=registration_number if registration_number else company.registration_number,
            gst_number=gst_number if gst_number else company.gst_number,
            address=address if address else company.address,
            logo=logo if logo else company.logo,
            contact_persons=json.loads(contact_persons) if contact_persons else company.contact_persons,
            user_limit=user_limit if user_limit else company.user_limit,
            country_id=country_id if country_id else company.country_id,
            state_id=state_id if state_id else company.state_id,
            city_id=city_id if city_id else company.city_id,
            is_deleted=is_deleted if is_deleted else company.is_deleted,
            industry_type_id=industry_type_id if industry_type_id else company.industry_type_id,
            globle_status_id=globle_status_id if globle_status_id else company.globle_status_id
        )

        return updated_company

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating company form: {str(e)}")
