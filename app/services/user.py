from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.auth import get_current_user
from fastapi import Depends, HTTPException
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings
from pydantic import constr, Field
from app.models.city import City
from app.models.state import State
from app.models.country import Country



class PasswordResetTokenGenerator:
    def __init__(self):
        self.serializer = URLSafeTimedSerializer(settings.jwt_secret_key)

    def make_token(self, user_id: int) -> str:
        """
        Generate a password reset token.
        """
        return self.serializer.dumps(user_id, salt="password-reset")
    
    def confirm_token(self, token: str, expiration: int = 3600) -> int:
        """
        Confirm and decode the token. Raise an exception if invalid or expired.
        """
        try:
            # The `max_age` argument should be passed here to enforce token expiration
            user_id = self.serializer.loads(token, salt="password-reset", max_age=expiration)
            print(f"Decoded User ID: {user_id}")
        except Exception as e:
            print(f"Token Validation Error: {e}")
            raise ValueError("Invalid or expired token")
        return user_id



def update_user_by_role(db: Session, user_id: int, updated_data: dict, current_user: User = Depends(get_current_user)):
    """
    Update a user based on the role of the logged-in user. Only 'superadmin' can update others.
    """
    # Ensure the logged-in user exists
    if not current_user:
        raise HTTPException(status_code=404, detail="Logged-in user not found")

    # Handle case where the role may be None and show 'null' when missing
    role_name = current_user.role.role_name.lower() if current_user.role else None  # Normalize role name or set to None

    if role_name == "superadmin":  # Case-insensitive check for superadmin role
        user_to_update = db.query(User).filter(User.user_id == user_id).first()
        if not user_to_update:
            raise HTTPException(status_code=404, detail="User to update not found")

        # Update the user with the new data only if the field is not None
        for key, value in updated_data.items():
            if hasattr(user_to_update, key) and value is not None:
                setattr(user_to_update, key, value)

        db.commit()
        db.refresh(user_to_update)
        return user_to_update
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to update this user")




def get_location_names(user: User, db: Session):
    """
    This method will return city name, state name, and country name for a given user.
    """
    city_name = None
    state_name = None
    country_name = None

    # Check if user has a related city, state, and country
    if user.city:
        city_name = user.city.name

    if user.state:
        state_name = user.state.name

    if user.country:
        country_name = user.country.name

    return city_name, state_name, country_name



