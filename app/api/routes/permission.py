from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.db.session import get_db
from app.utils.auth import get_current_user  
from app.services.permission import get_all_permission_service

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_permissions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission_name: Optional[str] = Query(None, description="Filter by permission"),
    permission_id: Optional[int] = Query(None, description="Filter by permission id")
):
   
    all_data = get_all_permission_service(db=db, current_user=current_user, permission_name=permission_name, permission_id=permission_id)
    
    return all_data