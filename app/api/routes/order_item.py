from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional
from app.models.user import User
from app.services.order_item import get_all_order_items,get_order_item_by_id,create_order_item,update_order_item,delete_order_item
from app.schemas.order_item import CreateOrderItemSchmea,UpdateOrderItemSchema, DeleteOrderItemSchema



router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_orderItem(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    
    orderItem_data = get_all_order_items(db=db, current_user=current_user)
    return orderItem_data
    

    
@router.get("/{order_item_id}",status_code=status.HTTP_200_OK)
def get_orderItem_by_id (order_item_id:int, db:Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    get_OrderItem_data = get_order_item_by_id(db=db, order_item_id=order_item_id,current_user=current_user)

    return get_OrderItem_data


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_orderItem(
    orderItem:CreateOrderItemSchmea,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    new_orderItem = create_order_item(db=db,order_item_service_data=orderItem,current_user=current_user)
        
    return new_orderItem
        


# @router.put("/{order_item_id}")
# async def update_existing_orderItem(
#     order_item_id: int,
#     update_orderItem: UpdateOrderItemSchema,
#     db: Session = Depends(get_db),
#     current_user: User= Depends(get_current_user)
    
#     ):
   
#     try: 
#         updated_orderItem = update_order_item(db=db, order_item_id=order_item_id, update_order_item_service_data=update_orderItem)
    
#         # If the company is not found, raise a 404 error
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Company not found : {str(e)}"
#         )
#     # Return the updated company data
#     return{
#         "message": "Address book was updated successfully",
#         "addressbooks": updated_orderItem
#         } 


@router.put("/{order_item_id}", status_code=status.HTTP_200_OK)
async def update_existing_orderItem(
    order_item_id: int,
    update_orderItem: UpdateOrderItemSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_orderItem = update_order_item(
        db=db, order_item_id=order_item_id, update_order_item_service_data=update_orderItem, current_user=current_user
    )
    
    return updated_orderItem



@router.delete("/{order_item_id}",  response_model= DeleteOrderItemSchema)
def delete_orderItem(
    order_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a order item by ID.
    """
   
    deleted_orderItem = delete_order_item(db, order_item_id)
    
    
    return {"message" : "Order item deleted successfully",}
