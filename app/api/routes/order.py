from fastapi import APIRouter, Depends, HTTPException, Query, status,File, UploadFile
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.utils.auth import get_current_user
from typing import Optional,List
from app.models.user import User
from app.models.order import OrderModel
from app.services.order import get_all_orders,get_order_by_id,create_order,update_order,delete_order,assign_driver_to_order,confirm_pickup,update_shipment_status,save_pod_upload_file,update_pod_file
from app.schemas.order import CreateOrderSchema,UpdateOrderSchema,DeleteOrderSchema,AssignDriverVehicleSchema,UpdateShipmentStatusSchema
from fastapi.responses import Response


router = APIRouter()

# BASE_FILE_URL = "http://localhost:8000/uploads/"


@router.get("/", status_code=status.HTTP_200_OK)
def get_all_order_endpoint(db: Session = Depends(get_db),current_user: User = Depends(get_current_user),shipment_status_name: str = None, docket_no: int = None,pincode:int = None ):
    
    order_data = get_all_orders(db=db, current_user=current_user, shipment_status_name = shipment_status_name, docket_no=docket_no, pincode=pincode)
    return order_data


@router.get("/{order_id}",status_code=status.HTTP_200_OK)
def get_order_by_id_endpoint (order_id:int, db:Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    get_Order_data = get_order_by_id(db=db, order_id=order_id,current_user=current_user)

    return get_Order_data


@router.put("/assign-driver", status_code=status.HTTP_200_OK)
def assign_driver_endpoint(
    order_ids: List[int], 
    request: AssignDriverVehicleSchema, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    
    responses = []

    # for order_id in order_ids: 
    updated_driverVehicle = assign_driver_to_order(db=db, order_ids=order_ids, assign_driver_vehicle=request, current_user=current_user)
        # responses.append(updated_driverVehicle)

    return updated_driverVehicle


@router.get("/confirm-pickup/{docket_no}", status_code=status.HTTP_200_OK)
def confirm_pickup_endpoint(
    docket_no: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return confirm_pickup(db=db, docket_no=docket_no, current_user=current_user)


@router.put("/{order_id}/update-shipment-status",status_code=status.HTTP_200_OK)
def update_shipment_status_endpoint(
    order_id: int,
    shipmentStatus: UpdateShipmentStatusSchema,
    db:Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return update_shipment_status(db=db, order_id=order_id, update_shipment_status_data=shipmentStatus,  current_user=current_user)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_new_order_endpoint(
    order:CreateOrderSchema,
    db: Session=Depends(get_db),
    current_user: User= Depends(get_current_user)
    
    ):
   
    new_order = create_order(db=db,order_service_data=order,current_user=current_user)
        
    return new_order

@router.put("/{order_id}", status_code=status.HTTP_200_OK)
async def update_order_endpoint(
    order_id: int,
    order_update: UpdateOrderSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    updated_order = update_order(
        db=db, order_id=order_id, update_order_service_data=order_update, current_user=current_user
    )
    
    return updated_order


@router.delete("/{order_id}",  response_model= DeleteOrderSchema)
def delete_order_endpoint(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Soft delete a order by ID.
    """
   
    delete_order(db, order_id, current_user)
    
    
    return {"message" : "Order deleted successfully",}


@router.post("/upload-pod/{order_id}")
async def upload_pod(order_id: int, file: UploadFile = File(...), db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    file_path = save_pod_upload_file(file)
    
    Uploaded_file = update_pod_file(db, order_id, file_path,current_user=current_user)
    if not Uploaded_file:
        return {"error": "Order not found"}
    
    return {"message": "File uploaded successfully", "file_path": file_path}


@router.get("/orders/{order_id}/pod")
def get_uploaded_file(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not order or not order.pod:
        return {"error": "File not found"}
    
    filename = order.pod.decode() if isinstance(order.pod, bytes) else order.pod

    file_url = f"http://localhost:8000/uploads/{filename}" 
    return {"file_url": file_url}

    # return Response(content=order.pod, media_type="application/octet-stream")



