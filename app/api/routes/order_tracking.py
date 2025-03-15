from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional
from app.models.user import User 
from app.services.order_tracking import get_all_order_tracking,get_order_tracking_by_id,create_order_tracking,update_order_tracking,delete_order_tracking
from app.schemas.order_tracking import CreateOrderTrackingSchema,UpdateOrderTrackingSchema,DeleteOrderTrackingSchema


router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
def get_all_orderTracking_endpoint(db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    
    orderTracking_data = get_all_order_tracking(db=db, current_user=current_user)
    return orderTracking_data


@router.get("/{order_tracking_id}",status_code=status.HTTP_200_OK)
def get_orderTracking_by_id_endpoint (order_tracking_id:int, db:Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    get_OrderTracking_data = get_order_tracking_by_id(db=db, order_tracking_id=order_tracking_id,current_user=current_user)

    return get_OrderTracking_data



@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_orderTracking_endpoint(
    orderTracking:CreateOrderTrackingSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    new_orderTracking = create_order_tracking(db=db,order_tracking_service_data=orderTracking,current_user=current_user)
        
    return new_orderTracking


@router.put("/{order_tracking_id}", status_code=status.HTTP_200_OK)
async def update_existing_orderTracking_endpoint(
    order_tracking_id: int,
    update_orderTracking: UpdateOrderTrackingSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_orderTracking = update_order_tracking(
        db=db, order_tracking_id=order_tracking_id, update_order_tracking_service_data=update_orderTracking, current_user=current_user
    )
    
    return updated_orderTracking


@router.delete("/{order_tracking_id}",  response_model= DeleteOrderTrackingSchema)
def delete_orderTracking_endpoint(
    order_tracking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a order tracking by ID.
    """
   
    delete_order_tracking(db, order_tracking_id)
    
    
    return {"message" : "Order tracking deleted successfully",}




