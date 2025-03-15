from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional
from app.models.user import User
from app.services.menu_privilege import get_all_menuPrivilegeService,get_all_menuList, create_menuPrivilegeService,update_menu_privileges,delete_menu_privilege
from app.schemas.menu_privilege import CreateMenuPrivilegeSchema,DeleteMenuPrivilegeSchema,UpdateMenuPrivilegeSchema


router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_list_menu_privilege_endpoint(
    db: Session = Depends(get_db),current_user: User = Depends(get_current_user), id:Optional[int] = Query(None, description="Filter by id"),
    role_name: Optional[str] = Query(None, description="Filter by role name"),
    menu_name: Optional[str] = Query(None, description="Filter by menu name"),):
    
    menu_privilege_data = get_all_menuPrivilegeService(db=db, current_user=current_user, id=id, role_name=role_name, menu_name=menu_name )
    return menu_privilege_data



@router.get("/menu-list", status_code=status.HTTP_200_OK)
def get_list_menu_list_endpoint(db: Session = Depends(get_db),current_user: User = Depends(get_current_user), role_id:Optional[int] = Query(None, description="Filter by role id"),):
    
    menu_privilege_data = get_all_menuList(db=db, current_user=current_user, role_id=role_id)
    return menu_privilege_data


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_menu_privilege_endpoint(
    menuPrivilege:CreateMenuPrivilegeSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):

    try:
        new_menu_privilege = create_menuPrivilegeService(db=db,menuPrivilege_service=menuPrivilege,current_user=current_user)
        
    
    except  Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error creating menu privilege:{str(e)}"
        )
        
    return{
        "menuPrivileges": new_menu_privilege
        }


@router.put("/{role_id}", status_code=status.HTTP_200_OK)
def update_existing_menuPrivilege_endpoint(
    role_id: int,
    menuPrivilege:UpdateMenuPrivilegeSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    
):
    
    updated_data = update_menu_privileges(db=db, menu_privilege_service=menuPrivilege, current_user=current_user, role_id=role_id)

    return updated_data


@router.delete("/{id}",  response_model= DeleteMenuPrivilegeSchema)
def delete_menuPrivilege_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a menu privilege by ID.
    """
   
    delete_menu_privilege(db, id, current_user)
    
    
    return {"message" : "Menu privilege deleted successfully",}


    