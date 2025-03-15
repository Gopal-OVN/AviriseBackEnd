from sqlalchemy.orm import Session
from fastapi import HTTPException,status
from typing import Optional
from app.models.user import User
from app.models.permission import PermissionModel


def get_all_permission_service(
    db: Session ,
    current_user: User ,
    permission_name: Optional[str],
    permission_id: int
    ):

    try:
        query = db.query(PermissionModel).filter(PermissionModel.is_deleted == False)
        
        if permission_name:
            query = query.filter(PermissionModel.permission_name == permission_name)
            
        
        if permission_id:
            query = query.filter(PermissionModel.permission_id == permission_id)
            
        total = query.count()
        permissions = query.all()

        if not permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No permission found"
            )
        
        return {
            "message": "Permission retrieved successfully",
            "total": total,
            "permissions": permissions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
