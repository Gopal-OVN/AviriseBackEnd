from sqlalchemy.orm import Session
import json
from fastapi import HTTPException,status
# from typing import Optional
from app.models.user import User
from app.models.order_item import OrderItemModel #,DimentionTypeEnum
from app.schemas.order_item import CreateOrderItemSchmea, UpdateOrderItemSchema



def get_all_order_items(db: Session , current_user:User):

    try:
        query = db.query(OrderItemModel).filter(OrderItemModel.is_deleted == False)

        order_items_data = query.all()

        if not order_items_data:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND ,
                detail = "No Order Item found"
            )
        

        return {
        "message": "Order items retrieved successfully",
        "total": len(order_items_data),
        "order_items": order_items_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_order_item_by_id(db: Session, order_item_id: int, current_user: User):
   
    get_orderItem = db.query(OrderItemModel).filter(OrderItemModel.order_item_id == order_item_id, OrderItemModel.is_deleted == False).first()

    if not get_orderItem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order item not found"
        )
    
    user_dict = {user.user_id: user.first_name for user in db.query(User).all()}
    get_orderItem.created_by_name = user_dict.get(get_orderItem.created_by, 'Unknown')
    get_orderItem.updated_by_name = user_dict.get(get_orderItem.updated_by, 'Unknown')


    return {
        "message": "Order item retrieved successfully",
        "order_item": get_orderItem
    }


def create_order_item(db: Session, order_item_service_data: CreateOrderItemSchmea, current_user: User):
    
    try:

        order_item_dict = order_item_service_data.dict(exclude_unset=True)
        order_item_dict["created_by"] = current_user.user_id
        new_order_item = OrderItemModel(**order_item_dict)
    
    # Add the new order_item to the database session and commit the changes
        db.add(new_order_item)
        db.commit()
        db.refresh(new_order_item)
        
        # Return the newly created order_item
        return {
            "message": "Order item created successfully",
            "order_item": new_order_item
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating order item: {str(e)}")





def update_order_item(
    db: Session, order_item_id: int, update_order_item_service_data: UpdateOrderItemSchema, current_user: User
):
    try:
        # Fetch existing order item
        update_orderItem = db.query(OrderItemModel).filter(
            OrderItemModel.order_item_id == order_item_id, OrderItemModel.is_deleted == False
        ).first()

        if not update_orderItem:
            raise HTTPException(status_code=404, detail="Order item not found")


        # Convert schema to dictionary and update only provided fields
        update_data = update_order_item_service_data.dict(exclude_unset=True)
        update_data["updated_by"] = current_user.user_id

        for key, value in update_data.items():
        #     if key == 'dimention_type' and value:
        #         value = DimentionTypeEnum(value)
            setattr(update_orderItem, key, value)

        # Commit changes to the database
        db.commit()
        db.refresh(update_orderItem)

        return {
        "message": "Order item updated successfully",
        "order_item": update_orderItem
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Error updating order item: {str(e)}")


def delete_order_item(db: Session, order_item_id: int):
   
    delete_orderItem = db.query(OrderItemModel).filter(OrderItemModel.order_item_id == order_item_id, OrderItemModel.is_deleted == False).first()
    
    if not delete_orderItem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order Item not found or already deleted"
            )
        
    
    
    delete_orderItem.is_deleted = True  # Mark as deleted (soft delete)
    delete_orderItem.is_active = False
    db.commit()  # Commit the changes
    db.refresh(delete_orderItem)  # Refresh to update the state
    
    return delete_orderItem

