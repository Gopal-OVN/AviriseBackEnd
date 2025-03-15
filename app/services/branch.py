from sqlalchemy.orm import Session
from app.models.branch import Branch as BranchModel
from app.models.company import Company as CompanyModel
from app.models.globle_status import GlobleStatus as StatusModel
from app.schemas.branch import BranchCreate, BranchUpdate
from fastapi import HTTPException, Depends
from app.utils.auth import get_current_user
from app.models.user import User
from app.services.common_validate_data import get_globle_status_name, validate_contact_number, get_user_name, validate_branch_name
import re

# Helper function to fetch globle_status_name
# def get_globle_status_name(db: Session, globle_status_id: int) -> str:
#     """Fetch globle_status_name from the Status model based on globle_status_id."""
#     globle_status = db.query(StatusModel).filter(StatusModel.id == globle_status_id).first()
#     return globle_status.name if globle_status else None

# # Helper function to fetch user name by user_id
# def get_user_name(db: Session, user_id: int) -> str:
#     """Fetch user's first name by user_id."""
#     user = db.query(User).filter(User.user_id == user_id).first()
#     return user.first_name if user else None

# # Function to validate branch name uniqueness
# def validate_branch_name(db: Session, name: str) -> bool:
#     """Ensure the branch name is unique."""
#     if db.query(BranchModel).filter(BranchModel.name == name).first():
#         raise HTTPException(status_code=400, detail="Branch name must be unique.")
#     return True

# # Function to validate contact number format
# def validate_contact_number(value: str) -> str:
#     """Ensure the contact number is exactly 10 digits."""
#     if not re.match(r'^\d{10}$', value):
#         raise HTTPException(status_code=400, detail="Contact number must contain exactly 10 digits and no special characters.")
#     return value

# CRUD function to create a new branch
def create_branch(db: Session, branch: BranchCreate, current_user: User):
    """Create a new branch with validation for name and contact number."""
    
    # Ensure that the global status ID is set to 1 if not provided
    if not branch.globle_status_id:
        branch.globle_status_id = 1
    
    # Validate branch name and contact number
    validate_branch_name(db, branch.name)
    validate_contact_number(branch.contact_number)

    # Create the branch and assign the created_by field using current_user.user_id
    db_branch = BranchModel(**branch.dict(exclude_unset=True))  # Exclude unset to ignore empty optional fields
    db_branch.created_by = current_user.user_id  # Assign created_by to the current user's ID
    db_branch.updated_by = current_user.user_id  # Initially set updated_by as created_by
    db.add(db_branch)  # Add branch to the session
    db.commit()  # Commit the transaction
    db.refresh(db_branch)  # Refresh to retrieve generated values

    # Fetch globle_status_name using the helper function
    db_branch.globle_status_name = get_globle_status_name(db, db_branch.globle_status_id)

    # Fetch created_by_name and updated_by_name using the helper function
    db_branch.created_by_name = get_user_name(db, db_branch.created_by)
    db_branch.updated_by_name = get_user_name(db, db_branch.updated_by)

    return db_branch

# CRUD function to get a branch by ID
def get_branch(db: Session, branch_id: int):
    """Get a branch by its ID."""
    db_branch = db.query(BranchModel).filter(BranchModel.id == branch_id, BranchModel.is_deleted == False).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    # Fetch globle_status_name using the helper function
    db_branch.globle_status_name = get_globle_status_name(db, db_branch.globle_status_id)

    # Fetch created_by_name and updated_by_name using the helper function
    db_branch.created_by_name = get_user_name(db, db_branch.created_by)
    db_branch.updated_by_name = get_user_name(db, db_branch.updated_by)

    return db_branch

# CRUD function to list all branches with pagination
def get_branches(db: Session, skip: int = 0, limit: int = 100):
    """Get all branches with pagination, excluding deleted ones."""
    branches = db.query(BranchModel).filter(BranchModel.is_deleted == False).offset(skip).limit(limit).all()

    # Fetch globle_status_name and user names for each branch
    for branch in branches:
        branch.globle_status_name = get_globle_status_name(db, branch.globle_status_id)
        branch.created_by_name = get_user_name(db, branch.created_by)
        branch.updated_by_name = get_user_name(db, branch.updated_by)

    return branches

# CRUD function to update a branch
def update_branch(db: Session, branch_id: int, branch: BranchUpdate, current_user: User):
    """Update a branch with validation for name and contact number."""
    db_branch = db.query(BranchModel).filter(BranchModel.id == branch_id, BranchModel.is_deleted == False).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    # Validate the company ID and branch name if they're updated
    if branch.company_id:
        db_company = db.query(CompanyModel).filter(CompanyModel.id == branch.company_id).first()
        if not db_company:
            raise HTTPException(status_code=400, detail="Invalid company_id: Company does not exist.")
    
    # Validate branch name and contact number if updated
    if branch.name and branch.name != db_branch.name:
        validate_branch_name(db, branch.name)
    if branch.contact_number and branch.contact_number != db_branch.contact_number:
        validate_contact_number(branch.contact_number)
    
    # Update provided fields
    for key, value in branch.dict(exclude_unset=True).items():
        setattr(db_branch, key, value)
    
    # Set updated_by to the current user's ID
    db_branch.updated_by = current_user.user_id
    
    db.commit()  # Commit the changes
    db.refresh(db_branch)  # Refresh to get the updated state

    # Fetch globle_status_name using the helper function
    db_branch.globle_status_name = get_globle_status_name(db, db_branch.globle_status_id)

    # Fetch created_by_name and updated_by_name using the helper function
    db_branch.created_by_name = get_user_name(db, db_branch.created_by)
    db_branch.updated_by_name = get_user_name(db, db_branch.updated_by)

    return db_branch

# CRUD function to soft delete a branch
def delete_branch(db: Session, branch_id: int):
    """Soft delete a branch by setting its is_deleted field to True."""
    db_branch = db.query(BranchModel).filter(BranchModel.id == branch_id, BranchModel.is_deleted == False).first()
    if not db_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    
    db_branch.is_deleted = True  # Soft delete the branch
    db.commit()  # Commit the changes
    db.refresh(db_branch)  # Refresh to get the updated state
    
    # Fetch created_by_name and updated_by_name using the helper function
    db_branch.created_by_name = get_user_name(db, db_branch.created_by)
    db_branch.updated_by_name = get_user_name(db, db_branch.updated_by)

    return db_branch
