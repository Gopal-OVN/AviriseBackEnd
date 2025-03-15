from fastapi import APIRouter, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.role import create_role, get_role, get_all_roles, delete_role, update_role
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.role import CreateRole, UpdateRole
from app.models.role import Role

# Initialize the API router for role-related endpoints
router = APIRouter()



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    role_name: str = Form(...),
    is_active: bool = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint to create a new role.

    - **role_name**: The name of the role to be created.
    - **is_active**: Indicates if the role is active or not.
    - **db**: Dependency to access the database session.
    - **current_user**: Dependency to get the current logged-in user.

    Returns a message and details of the newly created role.
    """
    try:
        # Create a `CreateRole` schema instance to pass to the database function
        role_data = CreateRole(role_name=role_name, is_active=is_active)

        # Call the `create_role` function to create the new role in the database
        new_role = create_role(
            db=db,
            role=role_data,
            current_user=current_user
        )
        # Get the created_by_name
        created_by_name = db.query(User).filter(User.user_id == new_role.created_by).first().first_name

        # Return the newly created role with the created_by_name
        return { 
            "message": "Role created successfully",
            "role": new_role, 
            "created_by_name": created_by_name 
        }
    except HTTPException as e:
        # If an HTTPException occurs, raise it
        raise e


@router.get("/{role_id}", status_code=status.HTTP_200_OK)
def get_role_endpoint(role_id: int, db: Session = Depends(get_db)):
    """
    Endpoint to retrieve a specific role by its ID.

    - **role_id**: The ID of the role to be retrieved.
    - **db**: Dependency to access the database session.

    Returns the role details if found, otherwise raises a 404 error.
    """
    # Query the database to find the role by ID, ensuring it's not marked as deleted
    role = db.query(Role).filter(Role.role_id == role_id, Role.is_deleted == False).first()

    
    # Add the created_by_name to the response
    # if role:
    #     role.created_by_name = db.query(User).filter(User.user_id == role.created_by).first().first_name

    
    role = get_role(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return {
        "message": "Role retrieved successfully",
        "role": role
    }


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_roles_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Endpoint to retrieve all available roles.

    - **db**: Dependency to access the database session.
    - **current_user**: Dependency to get the current logged-in user.

    Returns a list of roles or an appropriate message if no roles are found.
    """
    # Query the database to get all roles that are not marked as deleted
    roles = db.query(Role).filter(Role.is_deleted == False).all()

    
    # Add the created_by_name to the response
    # for role in roles:
    #     role.created_by_name = db.query(User).filter(User.user_id == role.created_by).first().first_name

    
    try:
        # Get all roles for the current user
        roles = get_all_roles(db, current_user)
    except HTTPException as e:
        # Handle exceptions and return an empty roles list with error message
        return {
            "message": e.detail,
            "roles": []
        }, e.status_code
    
    if not roles:
        return {
            "message": "No roles found in the database",
            "roles": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "Roles retrieved successfully",
        "roles": roles
    }


@router.put("/{role_id}", status_code=status.HTTP_200_OK)
def update_role_endpoint(
    role_id: int,
    role_name: str = Form(..., description="Updated name of the role"),
    is_active: bool = Form(..., description="Updated active status"),
    is_deleted: bool = Form(..., description="Updated deleted status"), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Update an existing role by ID.
    """
    # Construct the UpdateRole schema instance from the form data
    role_data = UpdateRole(role_name=role_name, is_active=is_active, is_deleted=is_deleted)

    # Call the `update_role` function to update the role in the database
    updated_role = update_role(db, role_id, role_data)

    return {
        "message": "Role updated successfully",
        "role": updated_role
    }


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_endpoint(
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a role by ID.
    """
    try:
        # Attempt to delete the role
        deleted_role = delete_role(db, role_id)
        return {
            "message": "Role deleted successfully"
        }
    except ValueError as e:
        # If a ValueError occurs, raise an HTTP exception with a 404 status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

