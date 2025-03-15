from sqlalchemy.orm import Session
import json
from fastapi import HTTPException,status
from fastapi import Query
from typing import Optional
from app.models.user import User
from app.models.role import Role
from app.models.permission import PermissionModel
from app.models.role_permission import RolePermissionModel
from app.schemas.role_permission import CreateRolePermissionSchema,UpdateRolePermissionSchema,GetRolePermissionSchema



def create_rolePermission(db: Session, rolePermission_service: CreateRolePermissionSchema, current_user: User):

    try:
        # existing_roles = db.query(Role).filter(Role.is_active == True, Role.is_deleted == False).all()
        # existing_permissions = db.query(PermissionModel).filter(PermissionModel.is_active == True, PermissionModel.is_deleted == False).all()


        role_permissions_data = rolePermission_service.dict()
        role_ids = role_permissions_data.get("role_ids", [])
        permission_ids = role_permissions_data.get("permission_ids", [])
        created_by = current_user.user_id

        new_role_permissions = []
        existing_role_permissions = []

        for role_id in role_ids:
            # if role_id not in existing_roles:
            #     raise ValueError(f"Role ID {role_id} does not exist.")
            
            for permission_id in permission_ids:
                existing_permission = (
                    db.query(RolePermissionModel)
                    .filter(RolePermissionModel.role_id == role_id,
                            RolePermissionModel.permission_id == permission_id)
                    .first() )
                
                if existing_permission:
                    if not existing_permission.is_deleted:  # Data already exists and is not deleted
                        # return {"message": "Role permission already exists", "role_permission": existing_permission}
                        # existing_role_permissions.append(existing_permission)
                        existing_role_permissions.append(GetRolePermissionSchema.from_orm(existing_permission))
                        continue  

                    existing_permission.is_deleted = False
                    existing_permission.is_active = True
                    db.commit()
                    db.refresh(existing_permission)
                    # return {"message": "Role permission reactivated successfully", "role_permission": existing_permission}
                    existing_role_permissions.append(GetRolePermissionSchema.from_orm(existing_permission))
                    continue
                
                role_permission = RolePermissionModel(
                    role_id=role_id,
                    permission_id=permission_id,
                    created_by=created_by,
                    is_active=True,
                    is_deleted=False
                )
                db.add(role_permission)
                new_role_permissions.append(role_permission)

        db.commit()

        for role_permission in new_role_permissions:
            db.refresh(role_permission)


        return {
                "message": "Permission create successfully",
                "role_permissions": new_role_permissions,
                "existing_role_permissions":existing_role_permissions
            }
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_all_rolePermission(
    db: Session ,
    current_user: User ,
    permission_name: Optional[str],
    role_permission_id: int
    ):

    try:
        query = db.query(RolePermissionModel).filter(
            RolePermissionModel.is_deleted == False
        )
        

        if permission_name:
            query = query.join(PermissionModel, (RolePermissionModel.permission_id == PermissionModel.permission_id))\
                        .filter(PermissionModel.permission_name == permission_name)
        
        if role_permission_id:
            query = query.filter(RolePermissionModel.role_permission_id == role_permission_id)

        total = query.count()
        roleRermissions = query.all()

        if not roleRermissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No permission found"
            )
        

        for rolePermission in roleRermissions:
            rolePermission.permission_name = db.query(PermissionModel.permission_name).filter(PermissionModel.permission_id == rolePermission.permission_id).scalar() 
            rolePermission.role_name = db.query(Role.role_name).filter(Role.role_id == rolePermission.role_id).scalar()  
        
        return {
            "message": "Permission retrieved successfully",
            "total": total,
            "role_permissions": roleRermissions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_role_permissions(
    db: Session, role_permission_service: UpdateRolePermissionSchema, current_user: User, role_id: int,
):
    try:
        existing_role_permissions = db.query(RolePermissionModel).filter(
            RolePermissionModel.role_id == role_id
        ).all()

        existing_role_permission_map = {
            role_permission.permission_id: role_permission for role_permission in existing_role_permissions
        }
        new_role_permission_ids = set(role_permission_service.permission_ids)  # Incoming permission IDs

        updated_role_permissions = []
        new_role_permissions = []

        # ✅ **Soft delete role_permissions that are removed from the request**
        for permission_id, role_permission in existing_role_permission_map.items():
            if permission_id not in new_role_permission_ids and not role_permission.is_deleted:
                role_permission.is_deleted = True
                role_permission.is_active = False
                updated_role_permissions.append(role_permission)

        # ✅ **Reactivate deleted role_permissions & Add new role_permissions**
        for permission_id in new_role_permission_ids:
            if permission_id in existing_role_permission_map:
                existing_permission = existing_role_permission_map[permission_id]

                if existing_permission.is_deleted:  # Reactivate soft-deleted entry
                    existing_permission.is_deleted = False
                    existing_permission.is_active = True
                    updated_role_permissions.append(existing_permission)

            else:
                # Add a new entry if it doesn't exist at all
                new_role_permission = RolePermissionModel(
                    role_id=role_id,
                    permission_id=permission_id,
                    created_by=current_user.user_id,
                    is_active=True,
                    is_deleted=False
                )
                db.add(new_role_permission)
                new_role_permissions.append(new_role_permission)

        db.commit()

        for role_permission in updated_role_permissions + new_role_permissions:
            db.refresh(role_permission)

        return {
            "message": "Role permissions updated successfully",
            "updated_role_permissions": updated_role_permissions,
            "new_role_permissions": new_role_permissions
        }
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def delete_role_permission(db: Session, role_permission_id: int):
   
    delete_rolePermission = db.query(RolePermissionModel).filter(RolePermissionModel.role_permission_id == role_permission_id, RolePermissionModel.is_deleted == False).first()
    
    if not delete_rolePermission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Role permission not found or already deleted"
            )
        
    
    
    delete_rolePermission.is_deleted = True  # Mark as deleted (soft delete)
    delete_rolePermission.is_active = False
    db.commit()  # Commit the changes
    db.refresh(delete_rolePermission)  # Refresh to update the state
    
    return delete_rolePermission


