from sqlalchemy.orm import Session
import json
from fastapi import HTTPException,status
# from typing import Optional
from app.models.user import User
from app.models.menu import MenuModel


def get_all_menus(db: Session , current_user:User):

    try:
        menu_data = db.query(MenuModel).filter(MenuModel.is_deleted == False).all()

        if not menu_data:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND ,
                detail = "No Menu  found"
            )

        return {
        "message": "Menu  retrieved successfully",
        "total": len(menu_data),
        "menu": menu_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
