from fastapi import Form
from typing import Optional
from app.schemas.user import UserUpdate


# Function to clean up the form data for blank fields
def get_user_update_from_form(
    first_name: Optional[str] = Form(None),
    last_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    country_id: Optional[int] = Form(None),
    state_id: Optional[int] = Form(None),
    city_id: Optional[int] = Form(None),
    pincode: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_deleted: Optional[bool] = Form(None),
    role_id: Optional[int] = Form(None),
    branch_id: Optional[int] = Form(None),
    company_id: Optional[int] = Form(None)
) -> UserUpdate:
    """
    Convert form data into UserUpdate schema.
    This function transforms form fields into a Pydantic model,
    with empty strings turned into None to handle empty values properly.
    """
    # Convert empty strings to None for all fields except email
    if first_name == "":
        first_name = None
    if last_name == "":
        last_name = None
    if phone_number == "":
        phone_number = None
    if address == "":
        address = None
    if pincode == "":
        pincode = None
    if country_id == "":
        country_id = None
    if state_id == "":
        state_id = None
    if city_id == "":
        city_id = None
    if is_active == "":
        is_active = None
    if is_deleted == "":
        is_deleted = None
    if role_id == "":
        role_id = None
    if branch_id == "":
        branch_id = None
    if company_id == "":
        company_id = None

    # Only allow email update if a new value is provided (not empty string)
    if email == "":
        email = None  # Do not set to None, avoid updating it if empty string is provided.

    return UserUpdate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone_number=phone_number,
        address=address,
        country_id=country_id,
        state_id=state_id,
        city_id=city_id,
        pincode=pincode,
        is_active=is_active,
        is_deleted=is_deleted,
        role_id=role_id,
        branch_id=branch_id,
        company_id=company_id
    )