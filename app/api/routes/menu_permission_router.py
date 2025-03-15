from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional
from app.models.user import User
from app.services.menu_permission_service import get_all_menuPermission

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_list_menu_permission_endpoint(
    db: Session = Depends(get_db),current_user: User = Depends(get_current_user),
    permission_name: Optional[str] = Query(None, description="Filter by permission name"),
    menu_name: Optional[str] = Query(None, description="Filter by menu name"),):
    
    menu_permission_data = get_all_menuPermission(db=db, current_user=current_user,  permission_name=permission_name, menu_name=menu_name )
    return menu_permission_data