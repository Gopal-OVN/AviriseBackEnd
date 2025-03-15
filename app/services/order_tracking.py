from sqlalchemy.orm import Session
import json
from fastapi import HTTPException,status
# from typing import Optional
from app.models.user import User
from app.models.order_tracking import OrderTrackingModel
from app.schemas.order_tracking import CreateOrderTrackingSchema,UpdateOrderTrackingSchema
from app.models.order import OrderModel


def get_all_order_tracking(db: Session , current_user:User):

    try:
        query = db.query(OrderTrackingModel).filter(OrderTrackingModel.is_deleted == False)

        order_tracking_data = query.all()

        if not order_tracking_data:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND ,
                detail = "No Order tracking found"
            )
        

        for orderTracking in order_tracking_data:
            orderTracking.docket = db.query(OrderModel.docket_no).filter(OrderModel.order_id == orderTracking.order_id).scalar()  
            orderTracking.comment = db.query(OrderModel.comment).filter(OrderModel.order_id == orderTracking.order_id).scalar()  
            orderTracking.pod = db.query(OrderModel.pod).filter(OrderModel.order_id == orderTracking.order_id).scalar()  


        return {
        "message": "Order tracking retrieved successfully",
        "total": len(order_tracking_data),
        "order_tracking": order_tracking_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_order_tracking_by_id(db: Session, order_tracking_id: int, current_user: User):
   
    get_orderTracking = db.query(OrderTrackingModel).filter(OrderTrackingModel.order_tracking_id == order_tracking_id, OrderTrackingModel.is_deleted == False).first()

    if not get_orderTracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order tracking not found"
        )
    
    user_dict = {user.user_id: user.first_name for user in db.query(User).all()}
    get_orderTracking.created_by_name = user_dict.get(get_orderTracking.created_by, 'Unknown')
    get_orderTracking.updated_by_name = user_dict.get(get_orderTracking.updated_by, 'Unknown')


    return {
        "message": "Order tracking retrieved successfully",
        "order_tracking": get_orderTracking
    }



def create_order_tracking(db: Session, order_tracking_service_data: CreateOrderTrackingSchema, current_user: User):
    
    try:

        order_tracking_dict = order_tracking_service_data.dict(exclude_unset=True)
        order_tracking_dict["created_by"] = current_user.user_id
        new_order_tracking = OrderTrackingModel(**order_tracking_dict)
    
    # Add the new order_tracking to the database session and commit the changes
        db.add(new_order_tracking)
        db.commit()
        db.refresh(new_order_tracking)
        
        # Return the newly created order_tracking
        return {
            "message": "Order tracking created successfully",
            "order_tracking": new_order_tracking
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating order tracking: {str(e)}")


def update_order_tracking(
    db: Session, order_tracking_id: int, update_order_tracking_service_data: UpdateOrderTrackingSchema, current_user: User
):
    try:
        # Fetch existing order tracking
        update_orderTracking = db.query(OrderTrackingModel).filter(
            OrderTrackingModel.order_tracking_id == order_tracking_id, OrderTrackingModel.is_deleted == False
        ).first()

        if not update_orderTracking:
            raise HTTPException(status_code=404, detail="Order tracking not found")


        update_data = update_order_tracking_service_data.dict(exclude_unset=True)
        update_data["updated_by"] = current_user.user_id

        for key, value in update_data.items():
           
            setattr(update_orderTracking, key, value)

        db.commit()
        db.refresh(update_orderTracking)

        return {
        "message": "Order tracking updated successfully",
        "order_tracking": update_orderTracking
    }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Error updating order tracking: {str(e)}")


def delete_order_tracking(db: Session, order_tracking_id: int):
   
    delete_orderTracking = db.query(OrderTrackingModel).filter(OrderTrackingModel.order_tracking_id == order_tracking_id, OrderTrackingModel.is_deleted == False).first()
    
    if not delete_orderTracking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order Tracking not found or already deleted"
            )
        
    
    
    delete_orderTracking.is_deleted = True  # Mark as deleted (soft delete)
    delete_orderTracking.is_active = False
    db.commit()  # Commit the changes
    db.refresh(delete_orderTracking)  # Refresh to update the state
    
    return delete_orderTracking

def get_all_docket(db: Session ,current_user: User ,):

    try:
        all_dockets = db.query(OrderTrackingModel).filter(OrderTrackingModel.order_id, OrderTrackingModel.is_deleted == False).all()

        

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

