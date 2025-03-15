from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.role_permission import RolePermissionModel
from app.schemas.role_permission import CreateRolePermissionSchema, DeleteRolePermissionSchema,UpdateRolePermissionSchema
from app.models.user import User
from app.db.session import get_db
from app.utils.auth import get_current_user  # Ensure this function exists
from app.services.role_permission import create_rolePermission, get_all_rolePermission, update_role_permissions, delete_role_permission

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_role_permission(
    rolePermission:CreateRolePermissionSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):

    try:
        new_role_permission = create_rolePermission(db=db,rolePermission_service=rolePermission,current_user=current_user)
        
    
    except  Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating role permission:{str(e)}"
        )
        
    return{
        "rolePermissions": new_role_permission
        }



@router.get("/", status_code=status.HTTP_200_OK)
def get_all_rolePermissions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    permission_name: Optional[str] = Query(None, description="Filter by permission"),
    role_permission_id: Optional[int] = Query(None, description="Filter by role permission id")
):
   
    all_data = get_all_rolePermission(db=db, current_user=current_user, permission_name=permission_name, role_permission_id=role_permission_id)
    
    return all_data

@router.put("/{role_id}", status_code=status.HTTP_200_OK)
def update_existing_rolePermission_endpoint(
    role_id: int,
    rolePermission:UpdateRolePermissionSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    
):
    
    updated_data = update_role_permissions(db=db, role_permission_service=rolePermission, current_user=current_user, role_id=role_id)

    return updated_data


@router.delete("/{role_permission_id}",  response_model= DeleteRolePermissionSchema)
def delete_rolePermission(
    role_permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a order item by ID.
    """
   
    deleted_rolePermission = delete_role_permission(db, role_permission_id)
    
    
    return {"message" : "Role Permission deleted successfully",}

