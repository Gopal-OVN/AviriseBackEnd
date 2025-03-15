import re
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from app.models.globle_status import GlobleStatus as StatusModel
from app.models.user import User
from app.models.role import Role
from app.models.branch import Branch as BranchModel
from app.db.session import get_db
from app.models.branch import Branch
from app.models.company import Company
from typing import Optional
from app.models.payment_mode import PaymentMode as PaymentModel




def get_role_name_from_id(role_id: int, db: Session) -> str:
    """
    Fetches the role name for a given role_id from the database.
    """
    role = db.query(Role).filter(Role.role_id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id provided."
        )
    return role.role_name

def validate_role_dependencies(role_id: Optional[int], company_id: Optional[int], branch_id: Optional[int], db: Session):
    """
    Validates if the given role_id requires company_id and branch_id.
    This is applicable only for roles like 'Customer'.
    """
    if role_id:
        role_name = get_role_name_from_id(role_id, db).lower()
        if role_name == "customer":
            if not company_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Company ID is required when the role is 'Customer'."
                )
            if not branch_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Branch ID is required when the role is 'Customer'."
                )
            # Verify branch belongs to company
            branch = db.query(Branch).filter(Branch.id == branch_id, Branch.company_id == company_id).first()
            if not branch:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Branch ID does not belong to the provided Company ID."
                )




# Helper function to fetch `globle_status_name` by `globle_status_id`
def get_globle_status_name(db: Session, globle_status_id: int) -> str:
    """
    Fetch `globle_status_name` from the Status model based on `globle_status_id`.
    """
    globle_status = db.query(StatusModel).filter(StatusModel.id == globle_status_id).first()
    return globle_status.name if globle_status else None



# Helper function to fetch `globle_status_name` by `status_id`
def get_status_name(db: Session, status_id: int) -> str:
    """
    Fetch `globle_status_name` from the GlobleStatus model based on `status_id`.
    """
    globle_status = db.query(StatusModel).filter(StatusModel.id == status_id).first()
    return globle_status.name if globle_status else None



# Helper function to fetch user first name by `user_id`
def get_user_name(db: Session, user_id: int) -> str:
    """
    Fetch the user's first name by `user_id`.
    """
    user = db.query(User).filter(User.user_id == user_id).first()
    return user.first_name if user else None


# Function to validate branch name uniqueness
def validate_branch_name(db: Session, name: str) -> bool:
    """
    Ensure the branch name is unique.
    """
    if db.query(BranchModel).filter(BranchModel.name == name).first():
        raise HTTPException(status_code=400, detail="Branch name must be unique.")
    return True


# Function to validate contact number format
def validate_contact_number(value: str) -> str:
    """
    Validator for contact number to ensure it's exactly 10 digits.
    """
    digits_only = ''.join(filter(str.isdigit, value))
    if len(digits_only) != 10:
        raise HTTPException(status_code=400, detail="Contact number must be exactly 10 digits.")
    return digits_only


# Validator for GST Number (15 characters, alphanumeric)
def gst_number_validator(value: str) -> str:
    """
    Validator for GST number to ensure it meets the required format.
    """
    if len(value) != 15 or not value.isalnum() or not value.isupper():
        raise ValueError("GST number must be 15 characters and alphanumeric.")
    return value


# Validator for PAN Number (10 characters, format: AAAAA9999A)
def pan_number_validator(value: str) -> str:
    """
    Validator for PAN number to ensure it meets the required format.
    """
    if value and (len(value) != 10 or not value.isupper() or not value[:5].isalpha() or not value[5:9].isdigit() or not value[9:].isalpha()):
        raise ValueError("PAN number must be 10 characters and in the format AAAAA9999A.")
    return value



# Function to validate payment name uniqueness
def validate_payment_name(db: Session, payment_name: str,description:str) -> bool:
    """
    Ensure the payment name is unique.
    """
    if db.query(PaymentModel).filter(PaymentModel.payment_name == payment_name,PaymentModel.description==description ).first():
        raise HTTPException(status_code=400, detail="Payment name must be unique.")
    return True



