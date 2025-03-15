from sqlalchemy.orm import Session
import json
from typing import Optional
from fastapi import HTTPException,status
from app.models.user import User
from app.models.menu_privilege import MenuPrivilegeModel 
from app.models.menu import MenuModel
from app.schemas.menu import MenuGet
from app.models.role import Role
from app.schemas.menu_privilege import CreateMenuPrivilegeSchema,UpdateMenuPrivilegeSchema,GetMenuPrivilegeSchema



def get_all_menuPrivilegeService(db: Session , current_user:User,  id:int , role_name:Optional[str], menu_name: Optional[str]=None ):
    # role_id:Optional[int], ,
    try:
        query = db.query(MenuPrivilegeModel).filter(MenuPrivilegeModel.is_deleted == False)

        if id:
            query = query.filter(MenuPrivilegeModel.id == id)
            
        if role_name:
            query = query.join(Role, (MenuPrivilegeModel.role_id == Role.role_id))\
                        .filter(Role.role_name == role_name)
            
        if menu_name:
            query = query.join(MenuModel, (MenuPrivilegeModel.menu_id == MenuModel.menu_id))\
                        .filter(MenuModel.menu_name == menu_name)


        menuPrivileges = query.all()
        
        if not menuPrivileges:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND ,
                detail = "Menu Privilege found"
            )

        for menuPrivilege in menuPrivileges:
            menuPrivilege.menu_name = db.query(MenuModel.menu_name).filter(MenuModel.menu_id == menuPrivilege.menu_id).scalar()  
            menuPrivilege.role_name = db.query(Role.role_name).filter(Role.role_id == menuPrivilege.role_id).scalar()  



        return {
        "message": "Menu Privilege retrieved successfully",
        "total": len(menuPrivileges),
        "menu_privilege": menuPrivileges
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

def get_all_menuList(db: Session , current_user:User,  role_id:Optional[int], menu_list: Optional[str]=None,  ):

    try:
        query = db.query(MenuPrivilegeModel).filter(MenuPrivilegeModel.is_deleted == False)

        # if menu_list:
        #     query = query.join(MenuModel, (MenuPrivilegeModel.menu_id == MenuModel.menu_id))\
        #                 .filter(MenuModel.menu_name == menu_name)
        if role_id:
            query = query.filter(MenuPrivilegeModel.role_id == role_id)
            

        menuPrivileges = query.all()
        
        if not menuPrivileges:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND ,
                detail = "Menu Privilege found"
            )

        result = []
        for menuPrivilege in menuPrivileges:
            menu_data = db.query(MenuModel).filter(MenuModel.menu_id == menuPrivilege.menu_id).first()

            if menu_data:
                menu_dict = MenuGet.from_orm(menu_data).dict()  # Convert SQLAlchemy model to dictionary

                # menuPrivilegeDict = {
                    # "men_privilage_id": menuPrivilege.id,
                    # "role_id": menuPrivilege.role_id,
                    # "menu_id": menuPrivilege.menu_id,
                    # "menu_details": menu_dict  # Use Pydantic schema here
                # }
                result.append(menu_dict)
                


        return {
        "message": "Menu Privilege retrieved successfully",
        "total": len(menuPrivileges),
        "menu_list": result
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def create_menuPrivilegeService(db: Session, menuPrivilege_service: CreateMenuPrivilegeSchema, current_user: User):

    try:
       
        menu_privilege_data = menuPrivilege_service.dict()
        role_ids = menu_privilege_data.get("role_ids", [])
        menu_ids = menu_privilege_data.get("menu_ids", [])
        created_by = current_user.user_id

        new_menu_privileges = []
        existing_menu_peivileges = []

        for role_id in role_ids:
           
            for menu_id in menu_ids:  # if one data exist but another one new ..create new and show existing
                existing_privilege = (
                    db.query(MenuPrivilegeModel)
                    .filter(MenuPrivilegeModel.role_id == role_id,
                            MenuPrivilegeModel.menu_id == menu_id)
                    .first() )
                
                if existing_privilege:
                    if not existing_privilege.is_deleted:  #if data alread exist and delete false
                        existing_menu_peivileges.append(GetMenuPrivilegeSchema.from_orm(existing_privilege))
                        continue
                    
                    existing_privilege.is_deleted = False  # if data exist and delete true
                    existing_privilege.is_active = True
                    db.commit()
                    db.refresh(existing_privilege)
                    existing_menu_peivileges.append(GetMenuPrivilegeSchema.from_orm(existing_privilege))
                    continue  
                
                menu_privilege = MenuPrivilegeModel(    #create data
                    role_id=role_id,
                    menu_id=menu_id,
                    created_by=created_by,
                    is_active=True,
                    is_deleted=False
                )
                db.add(menu_privilege)
                new_menu_privileges.append(menu_privilege)

        db.commit()

        for menu_privilege in new_menu_privileges:
            db.refresh(menu_privilege)


        return {
                "message": "Menu privilege create successfully",
                "menu_privileges": new_menu_privileges,
                "existing_menu_peivileges":existing_menu_peivileges
            }
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_menu_privileges(
    db: Session, menu_privilege_service: UpdateMenuPrivilegeSchema, current_user: User, role_id: int,
):
    try:

        existing_menu_privileges = db.query(MenuPrivilegeModel).filter(
            MenuPrivilegeModel.role_id == role_id
        ).all()

        existing_menu_privilege_map = {
            menu_privilege.menu_id: menu_privilege for menu_privilege in existing_menu_privileges
        }
        new_menu_privilege_ids = set(menu_privilege_service.menu_ids)  # Incoming menu_privilege IDs

        updated_menu_privileges = []
        new_menu_privileges = []

        # ✅ **Soft delete menu_privileges that are removed from the request**
        for menu_id, menu_privilege in existing_menu_privilege_map.items():
            if menu_id not in new_menu_privilege_ids and not menu_privilege.is_deleted:
                menu_privilege.is_deleted = True
                menu_privilege.is_active = False
                updated_menu_privileges.append(menu_privilege)

        # ✅ **Reactivate deleted menu_privileges & Add new menu_privileges**
        for menu_id in new_menu_privilege_ids:
            if menu_id in existing_menu_privilege_map:
                existing_menu = existing_menu_privilege_map[menu_id]

                if existing_menu.is_deleted:  # Reactivate soft-deleted entry
                    existing_menu.is_deleted = False
                    existing_menu.is_active = True
                    updated_menu_privileges.append(existing_menu)

            else:
                # Add a new entry if it doesn't exist at all
                new_menu_privilege = MenuPrivilegeModel(
                    role_id=role_id,
                    menu_id=menu_id,
                    created_by=current_user.user_id,
                    is_active=True,
                    is_deleted=False
                )
                db.add(new_menu_privilege)
                new_menu_privileges.append(new_menu_privilege)

        db.commit()

        for privilege in updated_menu_privileges + new_menu_privileges:
            db.refresh(privilege)

        return {
            "message": "Menu privileges updated successfully",
            "updated_menu_privileges": updated_menu_privileges,
            "new_menu_privileges": new_menu_privileges
        }
    
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




def delete_menu_privilege(db: Session, id: int, current_user: User,):
   
    delete_menuPrivilege = db.query(MenuPrivilegeModel).filter(MenuPrivilegeModel.id == id, MenuPrivilegeModel.is_deleted == False).first()
    
    if not delete_menuPrivilege:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Menu privilege not found or already deleted"
            )
        
    
    
    delete_menuPrivilege.is_deleted = True  # Mark as deleted (soft delete)
    delete_menuPrivilege.is_active = False
    db.commit()  # Commit the changes
    db.refresh(delete_menuPrivilege)  # Refresh to update the state
    
    return delete_menuPrivilege


