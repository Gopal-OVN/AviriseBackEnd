from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from app.schemas.branch import BranchCreate, BranchUpdate, Branch
from app.services.branch import create_branch, get_branch, get_branches, update_branch, delete_branch
from typing import List
from app.models.user import User

router = APIRouter()



@router.post("/", response_model=Branch, status_code=status.HTTP_201_CREATED)
async def create_new_branch(
    branch: BranchCreate, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(get_current_user)
    ):
    """
    Endpoint to create a new branch.

    Validates the input data and creates a new branch in the database,
    associating the current authenticated user as the creator of the branch.
    Returns the created branch details.
    """
    # Create the branch in the database after validating the input data
    created_branch = create_branch(db=db, branch=branch, current_user=current_user)
    return created_branch


@router.get("/{branch_id}", response_model=Branch)
async def get_single_branch(branch_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a single branch by its ID.

    Fetches the branch data from the database using the provided branch ID.
    Returns the branch details if found.
    """
    # Retrieve the branch from the database
    branch = get_branch(db=db, branch_id=branch_id)
    return branch


@router.get("/", response_model=List[Branch])
async def get_all_branches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a list of all branches.

    Fetches a list of branches from the database with optional pagination
    based on the provided skip and limit values. Returns the list of branches.
    """
    # Retrieve the list of branches with pagination
    branches = get_branches(db=db, skip=skip, limit=limit)
    return branches


@router.put("/{branch_id}", response_model=Branch)
async def update_existing_branch(
    branch_id: int, 
    branch: BranchUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint to update an existing branch.

    Updates the branch data in the database using the provided branch ID and
    the new data. Returns the updated branch details.
    """
    # Pass current_user to the update_branch function
    updated_branch = update_branch(db=db, branch_id=branch_id, branch=branch, current_user=current_user)
    return updated_branch


@router.delete("/{branch_id}", response_model=Branch)
async def soft_delete_branch(
    branch_id: int, 
    db: Session = Depends(get_db)
    ):
    """
    Endpoint to soft delete a branch by its ID.

    Marks the branch as deleted in the database without removing the data permanently.
    Returns a success message indicating the branch was deleted.
    """
    # Soft delete the branch in the database
    deleted_branch = delete_branch(db=db, branch_id=branch_id)
    return {"message": "Branch deleted successfully"}

