from fastapi import APIRouter, HTTPException, Depends,status, Query
# from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.branch import Branch
from app.models.company import Company
from app.models.role import Role
from app.models.globle_status import GlobleStatus
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.utils.auth import get_current_user
# from app.forms.user_form import get_user_update_from_form 
from app.utils.password import hash_password, generate_strong_password
# from app.utils.jwt import create_access_token
from datetime import datetime
# from app.core.config import settings
from app.utils.email import  send_welcome_email
from app.services.user import  update_user_by_role
# from fastapi.responses import JSONResponse
from app.services.common_validate_data import  validate_role_dependencies, get_role_name_from_id
# import uuid
# import re
from app.models.drivers import DriverModel


router = APIRouter()



@router.post("/", status_code=201, response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user after validating input, ensuring dependencies, generating a password, and sending a welcome email.
    
    If the email is already registered or if the company or branch does not exist, an error is raised.
    """
    # Ensure status_id is set
    if not user.status_id:
        user.status_id = 1

    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role dependencies
    validate_role_dependencies(user.role_id, user.company_id, user.branch_id, db)

    # Validate company and branch
    if user.company_id:
        company = db.query(Company).filter(Company.id == user.company_id, Company.is_deleted == False).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company ID does not exist or is deleted."
            )
    if user.branch_id:
        branch = db.query(Branch).filter(Branch.id == user.branch_id, Branch.is_deleted == False).first()
        if not branch:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Branch ID does not exist or is deleted."
            )

    # Generate and hash password
    generated_password = user.password or generate_strong_password()
    hashed_password = hash_password(generated_password)

    # Create user
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        license_no=user.license_no,
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        address=user.address,
        country_id=user.country_id,
        state_id=user.state_id,
        city_id=user.city_id,
        pincode=user.pincode,
        role_id=user.role_id,
        branch_id=user.branch_id,
        company_id=user.company_id,
        status_id=user.status_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
      # If the user is a driver, create a corresponding entry in DriverModel
    role_name = get_role_name_from_id(user.role_id, db)  # Helper function to get role name
    if role_name.lower() == "driver":
        new_driver = DriverModel(
            user_id=new_user.user_id,
            name=f"{new_user.first_name} {new_user.last_name}",
            license_no=new_user.license_no,
            created_by=new_user.user_id,  
            is_active=True
        )
        db.add(new_driver)
        db.commit()


    # Send welcome email
    send_welcome_email(
        to_email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=generated_password
    )

    return new_user





@router.get("/users", status_code=200)
def get_users_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    role_id: int = None,
    company_id: int = None,
    branch_id: int = None,
    role_name: str = None,
    company_name: str = None,
    branch_name: str = None,
    email: str = None,
    first_name: str = None,
    last_name: str = None,
    ):
    """
    Retrieves a paginated list of users with optional filters for role, company, branch, and user information.
    """
    # Base query with necessary joins for related tables
    query = db.query(User).join(Role, User.role_id == Role.role_id, isouter=True) \
                           .join(Branch, User.branch_id == Branch.id, isouter=True) \
                           .join(Company, User.company_id == Company.id, isouter=True) \
                           .join(GlobleStatus, User.status_id == GlobleStatus.id, isouter=True)

    # Apply filters based on the provided parameters
    if role_id:
        query = query.filter(User.role_id == role_id)
    if company_id:
        query = query.filter(User.company_id == company_id)
    if branch_id:
        query = query.filter(User.branch_id == branch_id)
    if role_name:
        query = query.filter(Role.role_name.ilike(f"%{role_name}%"))
    if company_name:
        query = query.filter(Company.name.ilike(f"%{company_name}%"))
    if branch_name:
        query = query.filter(Branch.name.ilike(f"%{branch_name}%"))
    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))
    if first_name:
        query = query.filter(User.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(User.last_name.ilike(f"%{last_name}%"))
    
    # Filter for non-deleted users
    query = query.filter(User.is_deleted == False)

    # Total number of users after applying filters
    total_users = query.count()

    # Apply pagination
    users = query.offset((page - 1) * page_size).limit(page_size).all()

    # Default status if no status found
    default_status = db.query(GlobleStatus).filter(GlobleStatus.id == 1).first()
    default_status_name = default_status.name if default_status else "Active"

    # Create response with users and metadata
    response = {
        "total": total_users,
        "page": page,
        "page_size": page_size,
        "users": [
            {
                **UserOut.from_orm(user).dict(),  # Serialize user data
                "role_name": user.role.role_name if user.role else None,
                "branch_name": user.branch.name if user.branch else None,
                "company_name": user.company.name if user.company else None,
                "status_id": user.status.id if user.status else 1,
                "status_name": user.status.name if user.status else default_status_name,  # Adding status_name
            }
            for user in users
        ],
    }

    return response


@router.get("/profile", status_code=200, response_model=UserOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    """
    Retrieves the profile information of the currently authenticated user.

    Returns:
        A dictionary containing the user's details, including status_name.
    """
    # Fetch the current user along with the related status information
    user = (
        db.query(User)
        .join(GlobleStatus, User.status_id == GlobleStatus.id, isouter=True)
        .filter(User.user_id == current_user.user_id, User.is_deleted == False)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prepare the response with status_name
    user_data = UserOut.from_orm(user).dict()
    user_data["status_id"] = user.status_id  # Include status_id in the response
    user_data["status_name"] = user.status.name.upper() if user.status else "ACTIVE"  # Default to "ACTIVE"

    return user_data


@router.put("/update/profile", response_model=UserOut, status_code=200)
def update_profile(
    user_update: UserUpdate,  # JSON input directly
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ):
    """
    Updates the authenticated user's profile, allowing partial updates. 
    Validates and modifies only the provided fields in the request body.
    """
    # Fetch the current user from the database
    user = (
        db.query(User)
        .join(GlobleStatus, User.status_id == GlobleStatus.id, isouter=True)
        .filter(User.user_id == current_user.user_id, User.is_deleted == False)
        .first()
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert Pydantic model to dictionary and exclude fields with None values
    update_data = user_update.dict(exclude_none=True)

    # Validate email (if present) for empty string
    if "email" in update_data and not update_data["email"].strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email cannot be an empty string. Please provide a valid email address.",
        )

    # Set default `status_id` if not provided
    if "status_id" not in update_data or update_data["status_id"] is None:
        update_data["status_id"] = user.status_id or 1  # Default to 1 (Active status)

    # Validate role dependencies (if role_id is provided)
    if "role_id" in update_data:
        new_role_id = update_data["role_id"]

        # Use existing company_id and branch_id if not provided in the update
        company_id = update_data.get("company_id", user.company_id)
        branch_id = update_data.get("branch_id", user.branch_id)

        # Call the role dependency validation
        validate_role_dependencies(new_role_id, company_id, branch_id, db)

    # Dynamically update the user object
    for key, value in update_data.items():
        setattr(user, key, value)

    # Update last login time
    user.last_login = datetime.now()

    # Commit the changes to the database
    db.commit()
    db.refresh(user)

    # Return the updated user data with status_id and status_name
    updated_user_data = UserOut.from_orm(user).dict()
    updated_user_data["status_id"] = user.status_id  # Fetch status_id from User model
    updated_user_data["status_name"] = user.status.name.upper() if user.status else "ACTIVE"  # Default to "ACTIVE"

    return updated_user_data





@router.get("/{user_id}", response_model=UserOut, status_code=200)
def get_user(user_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves a user by their user_id if they exist.
    
    - user_id: ID of the user to retrieve.
    """
    user = db.query(User).join(GlobleStatus, User.status_id == GlobleStatus.id, isouter=True) \
                         .filter(User.user_id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Add status_name to the response
    user_data = UserOut.from_orm(user).dict()
    user_data["status_name"] = user.status.name if user.status else None
    
    return user_data





@router.delete("/delete-self", status_code=200)
def delete_self(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Soft deletes the current user's account (marks as deleted).
    The current user can only delete their own account.
    """
    # Fetch the current user from the database
    user = db.query(User).filter(User.user_id == current_user.user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mark the user as deleted (soft delete)
    user.is_deleted = True
    user.deleted_at = datetime.now()
    
    # Commit the changes
    db.commit()
    
    return {"message": "Your account has been deleted successfully."}


@router.delete("/delete-user/{user_id}", status_code=200)
def delete_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """
    Deletes a user by their ID. This action can only be performed by a user with the 'superuser' role.
    """
    
    
    # Check if the current user has a role and if the role is 'superuser' (case insensitive)
    print(f"Current User Role: {current_user.role.role_name if current_user.role else 'None'}")

    if current_user.role is None or current_user.role.role_name.lower() != 'superadmin':
        raise HTTPException(status_code=403, detail="You do not have permission to delete this user.")
    
    # Fetch the user to be deleted by ID
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mark the user as deleted (soft delete)
    user.is_deleted = True
    user.deleted_at = datetime.now()
    
    
        # Check if user is a driver and perform soft delete
    driver = db.query(DriverModel).filter(DriverModel.user_id == user_id).first()
    if driver:
        driver.is_deleted = True
        driver.deleted_at = datetime.now()

    
    # Commit the changes
    db.commit()
    
    return {"message": f"User with ID {user_id} has been deleted successfully."}


@router.put("/update-user/{user_id}")
def update_user(
    user_id: int, 
    updated_data: UserUpdate,  # Using the UserUpdate Pydantic model
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Updates the user details by user ID with provided data. 
    Removes driver record if the user is no longer a driver.
    """
    # Get the existing user
    existing_user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the previous role before update
    previous_role_name = get_role_name_from_id(existing_user.role_id, db).lower()

    # Update the user details
    updated_user = update_user_by_role(
        db=db,
        user_id=user_id,
        updated_data=updated_data.dict(),
        current_user=current_user
    )

    # Fetch updated user
    user = db.query(User).join(GlobleStatus, User.status_id == GlobleStatus.id, isouter=True) \
                          .filter(User.user_id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Return updated user data with status_name
    updated_user_data = UserOut.from_orm(user).dict()
    
    # Get the updated role name
    updated_role_name = get_role_name_from_id(user.role_id, db).lower()

    # Handle driver record
    if updated_role_name == "driver":
        # Check if a driver record exists
        driver = db.query(DriverModel).filter(DriverModel.user_id == user_id).first()
        if driver:
            # Update existing driver
            driver.name = f"{updated_data.first_name} {updated_data.last_name}" if updated_data.first_name or updated_data.last_name else driver.name
            driver.license_no = updated_data.license_no if updated_data.license_no else driver.license_no
            db.commit()
            db.refresh(driver)
        else:
            # Create a new driver record if it doesn't exist
            new_driver = DriverModel(
                user_id=user_id,
                name=f"{updated_data.first_name} {updated_data.last_name}",
                license_no=updated_data.license_no,
                created_by=current_user.user_id,
                is_active=True
            )
            db.add(new_driver)
            db.commit()
            db.refresh(new_driver)

    elif previous_role_name == "driver" and updated_role_name != "driver":
        # If the user was a driver but is no longer a driver, delete the driver record
        db.query(DriverModel).filter(DriverModel.user_id == user_id).delete()
        db.commit()

    return {"message": "User updated successfully", "user": updated_user_data}
