from fastapi import APIRouter, Depends, HTTPException,Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.utils.jwt import create_access_token
from app.utils.password import verify_password
from datetime import timedelta
from app.utils.email import send_email, render_email_template
from app.utils.password import hash_password, verify_password, validate_password
from app.core.config import settings
from datetime import  timedelta
from app.utils.jwt import create_access_token
from app.utils.auth import get_current_user
from app.services.user import PasswordResetTokenGenerator
from app.models.role_permission import RolePermissionModel
from app.models.permission import PermissionModel
from app.models.menu import MenuModel
from app.models.menu_privilege import MenuPrivilegeModel







router = APIRouter()

# @router.post("/login")
# def login(email: str, password: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == email).first()
#     if not user or not verify_password(password, user.password_hash):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )

#     access_token = create_access_token(
#         data={"sub": user.email}, expires_delta=timedelta(minutes=30)
#     )
#     return {"access_token": access_token, "token_type": "bearer"}



@router.post("/login", status_code=200)
def login( email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    """
    Authenticates the user by verifying their email and password, and generates a JWT access token if valid credentials are provided.
    """
    # Retrieve user from the database by email
    user = db.query(User).filter(User.email == email).first()
    # Check if the user exists and if the password is valid
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    
    # Fetch role-based permissions
    role_permissions = (
        db.query(PermissionModel.permission_name)
        .join(RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.permission_id)
        .filter(RolePermissionModel.role_id == user.role_id, RolePermissionModel.is_deleted == False)
        .all()
    )

    permissions_list = [perm[0] for perm in role_permissions]

    menu_privilage = (
        db.query(MenuModel.menu_name)
        .join(MenuPrivilegeModel, MenuPrivilegeModel.menu_id == MenuModel.menu_id)
        .filter(MenuPrivilegeModel.role_id == user.role_id, MenuPrivilegeModel.is_deleted == False)
        .all()
    )

    menu_list = [perm[0] for perm in menu_privilage]
    # Create an access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )

    me = user
   
    # Return the access token and token type
    return {"access_token": access_token, "token_type": "bearer", "permissions": permissions_list, "menus": menu_list, "me": me}


@router.put("/update-password", status_code=200)
def update_password(
    old_password: str, 
    new_password: str, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
    ):
    """
    Updates the current user's password if the old password is valid,
    the new password is different from the old one, and it meets strength requirements.
    
    Args:
    - old_password: Current password to validate against.
    - new_password: New password to set.

    Returns:
    - Success message if updated.
    """
    
    # Check if the old password is correct
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect.")
    
    # Check if the new password is the same as the old password
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="New password must be different from the old password.")
    
    # Validate the new password strength
    if not validate_password(new_password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long, contain an uppercase letter, a special character, and a number."
        )
    
    # Hash the new password and update it in the database
    hashed_password = hash_password(new_password)
    current_user.password_hash = hashed_password
    db.commit()
    return {"msg": "Password updated successfully"}



@router.post("/forgot-password", status_code=200)
def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    """
    Generates and sends a password reset link to the user's email.
    The link contains a unique token to allow the user to reset their password.
    """
    # Check if user with the provided email exists
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # If no user is found, raise an HTTP error
        raise HTTPException(status_code=404, detail="User not found")
    
    # Initialize token generator to create a reset token
    token_generator = PasswordResetTokenGenerator()
    reset_token = token_generator.make_token(user.user_id)
    
    # Use settings for domain URL
    domain_url = settings.domain_url 
    
    # Create the password reset link with the token embedded
    reset_link = f"{domain_url}/reset-password?token={reset_token}"
    
    # Prepare context for the email template
    context = {
        'reset_url': reset_link
    }

    # Render the email body from the template
    email_body = render_email_template('password_reset_email.html', context)
    
    # Send the reset link to the user's email address
    send_email(to_email=email, subject="Reset Your Password", body=email_body)
    
    # Return a success message to the client
    return {"message": "Password reset link sent to your email"}

@router.post("/reset-password", status_code=200)
def reset_password(token: str = Form(...), new_password: str = Form(...), db: Session = Depends(get_db)):
    """
    Resets the user's password using a valid token.
    The token is verified and if valid, the password is updated for the user.
    """
    # Initialize token generator to confirm the reset token
    token_generator = PasswordResetTokenGenerator()
    
    try:
        # Decode and validate the token, returning the user ID
        user_id = token_generator.confirm_token(token)
    except ValueError as e:
        # If the token is invalid or expired, raise an error
        raise HTTPException(status_code=400, detail=str(e))
    
    # Find the user by the decoded user ID
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        # If no user is found, raise an HTTP error
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find the user by the decoded user ID
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        # If no user is found, raise an HTTP error
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the new password is strong enough using the validate_password function
    if not validate_password(new_password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long, contain an uppercase letter, a special character, and a number."
        )
    
    # Hash the new password and update it in the database
    user.password_hash = hash_password(new_password)
    
    # Commit the changes to the database
    db.commit()
    
    # Return a success message indicating password reset
    return {"message": "Password reset successful"}


