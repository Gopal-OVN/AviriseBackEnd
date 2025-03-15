from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.role import Role
from app.models.user import User
from app.schemas.role import CreateRole, UpdateRole
from datetime import datetime


def get_role(db: Session, role_id: int):
    """Get a role by ID."""
    # Query the database to find the role by ID, ensuring it's not marked as deleted
    return db.query(Role).filter(Role.role_id == role_id, Role.is_deleted == False).first()


def get_all_roles(db: Session, current_user: User):
    """Get all active roles."""
    # Query the database to get all roles that are not marked as deleted
    roles = db.query(Role).filter(Role.is_deleted == False).all()
    
    # If no roles are found, raise a 404 error
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No roles found"
        )
    
    # Return the list of roles if found
    return roles

def create_role(db: Session, role: CreateRole, current_user: User):
    """Create a new role."""
    # Check if the role already exists based on the role name
    if db.query(Role).filter(Role.role_name == role.role_name).first():
        # If role exists, raise an error
        raise HTTPException(status_code=400, detail="Role already exists")
    
    # Create a new role instance with provided data
    new_role = Role(
        role_name=role.role_name,
        is_active=role.is_active,
        created_by=current_user.user_id,  # Set the user who created the role
    )
    
    # Add the new role to the database session and commit the changes
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    # Return the newly created role
    return new_role

def delete_role(db: Session, role_id: int):
    """Soft delete a role."""
    # Query the role to be deleted, ensuring it isn't already deleted
    role = db.query(Role).filter(Role.role_id == role_id, Role.is_deleted == False).first()
    
    # If role is not found or already deleted, raise a 404 error
    if not role:
        raise HTTPException(status_code=404, detail="Role not found or already deleted")
    
    # Mark the role as deleted and inactive
    role.is_deleted = True
    role.is_active = False
    db.commit()
    db.refresh(role)
    
    # Return the soft-deleted role
    return role

def update_role(db: Session, role_id: int, role_data: UpdateRole):
    """Update an existing role."""
    # Query the role to update, ensuring it isn't marked as deleted
    role = db.query(Role).filter(Role.role_id == role_id, Role.is_deleted == False).first()
    
    # If role is not found, raise a 404 error
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    # Update the role's fields with new data
    role.role_name = role_data.role_name
    role.is_active = role_data.is_active
    role.is_deleted = role_data.is_deleted
    role.updated_at = datetime.utcnow()  # Set the update timestamp
    db.commit()
    db.refresh(role)
    
    # Return the updated role
    return role
