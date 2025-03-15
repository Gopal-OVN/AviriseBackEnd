from fastapi import APIRouter, HTTPException, Depends, status, Form
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.menu import  get_all_menus
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.menu import MenuModel

# Initialize the API router for menu-related endpoints
router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_menus_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
   
    # Query the database to get all menus that are not marked as deleted
    menu_data = db.query(MenuModel).filter(MenuModel.is_deleted == False).all()

    
    if not menu_data:
        return {
            "message": "No menus found in the database",
            "menus": []
        }, status.HTTP_204_NO_CONTENT

    return {
        "message": "Menus retrieved successfully",
        "menus": menu_data
    }
