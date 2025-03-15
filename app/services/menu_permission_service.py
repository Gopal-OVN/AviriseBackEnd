from sqlalchemy.orm import Session
import json
from fastapi import HTTPException,status
from fastapi import Query
from typing import Optional
from app.models.user import User
from app.models.role import Role
from app.models.role_permission import RolePermissionModel
from app.models.menu_privilege import MenuPrivilegeModel
from app.models.permission  import PermissionModel
from app.models.menu import MenuModel
from collections import defaultdict



def get_all_menuPermission(
    db: Session ,
    current_user: User ,
    permission_name: Optional[str],
    menu_name: Optional[str]
    ):

    try:
        # Get all roles
        all_roles = db.query(Role).filter(Role.is_deleted == False).all()

        # Get role permissions with role and permission details
        role_permissions_query = db.query(
            RolePermissionModel.role_permission_id,
            RolePermissionModel.role_id,
            Role.role_name,
            RolePermissionModel.permission_id,
            PermissionModel.permission_name
        ).join(PermissionModel, RolePermissionModel.permission_id == PermissionModel.permission_id)\
         .join(Role, RolePermissionModel.role_id == Role.role_id)\
         .filter(RolePermissionModel.is_deleted == False)

        if permission_name:
            role_permissions_query = role_permissions_query.filter(PermissionModel.permission_name == permission_name)

        # Get menu privileges with menu details
        menu_privileges_query = db.query(
            MenuPrivilegeModel.id,
            MenuPrivilegeModel.menu_id,
            MenuModel.menu_name,
            MenuPrivilegeModel.role_id
        ).join(MenuModel, MenuPrivilegeModel.menu_id == MenuModel.menu_id)\
         .filter(MenuPrivilegeModel.is_deleted == False)

        if menu_name:
            menu_privileges_query = menu_privileges_query.filter(MenuModel.menu_name == menu_name)

        # Execute queries
        role_permissions = role_permissions_query.all()
        menu_privileges = menu_privileges_query.all()

        if not role_permissions and not menu_privileges:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No permissions or menu privileges found"
            )

        # Group permissions by role_id
        role_permissions_dict = defaultdict(list)
        for rp in role_permissions:
            role_permissions_dict[rp.role_id].append({
                "permission_id": rp.permission_id,
                "permission_name": rp.permission_name
            })

        # Group menu names by role_id
        role_menus_dict = defaultdict(list)
        for mp in menu_privileges:
            role_menus_dict[mp.role_id].append({
                "menu_id": mp.menu_id,
                "menu_name": mp.menu_name
            })

        # Format the response
        menu_permissions_data = [
            {
                "role_id": role_id,
                "role_name": next((r.role_name for r in all_roles if r.role_id == role_id), None),
                "permissions": role_permissions_dict.get(role_id, []),  # List of permission names
                "menus": role_menus_dict.get(role_id, [])  # List of menu names
            }
            for role_id in set(role_permissions_dict.keys()) | set(role_menus_dict.keys())
        ]

        return {
            "message": "Permissions and menu privileges retrieved successfully",
            "menu_permissions": menu_permissions_data
        }
        
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
