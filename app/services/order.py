from sqlalchemy.orm import Session
import json

from typing import Optional,List
from fastapi import HTTPException,status,UploadFile
from app.models.user import User
from app.models.order import OrderModel,PaymentTypeEnum,DimensionTypeEnum
from app.schemas.order import CreateOrderSchema,UpdateOrderSchema, AssignDriverVehicleSchema,UpdateShipmentStatusSchema
from app.models.order_item import OrderItemModel
from app.schemas.order_item import GetOrderItemSchema
from app.models.order_tracking import OrderTrackingModel
from app.schemas.order_tracking import GetOrderTrackingSchema
from app.models.user import User
from app.models.service_type import ServiceType
from app.models.payment_mode import PaymentMode
from app.models.address_book import AddressBookModel
from app.models.parcel_type import ParcelType
from app.models.shipment_status import ShipmentStatusModel
from app.models.drivers import DriverModel
from app.models.vehicle import VehicleModel
from sqlalchemy.exc import SQLAlchemyError
import os
import shutil

# from fastapi import UploadFile




def get_all_orders(db: Session , current_user:User, 
    shipment_status_name: str = None,
    docket_no: int = None,
    pincode:int = None
    ):

    try:
        query = db.query(OrderModel).filter(OrderModel.is_deleted == False)

        if shipment_status_name:
            query = query.join(ShipmentStatusModel, OrderModel.shipment_status_id == ShipmentStatusModel.shipment_status_id)\
                         .filter(ShipmentStatusModel.shipment_status_name == shipment_status_name)
       
        if docket_no:
            query = query.filter(OrderModel.docket_no == docket_no)

        if pincode:
            query = query.join(AddressBookModel, (OrderModel.receiver_address_book_id == AddressBookModel.address_book_id) | 
                        (OrderModel.sender_address_book_id == AddressBookModel.address_book_id))\
                        .filter(AddressBookModel.pincode == pincode)

        orders_data = query.all()

        if not orders_data:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND ,
                detail = "No Order found"
            )
        
        for order in orders_data:
            order.customer_name = db.query(User.first_name).filter(User.user_id == order.customer_id).scalar()  
            order.service_type_name = db.query(ServiceType.name).filter(ServiceType.service_id == order.service_type_id).scalar()
            order.payment_mode_name = db.query(PaymentMode.payment_name).filter(PaymentMode.payment_id == order.payment_mode_id).scalar()
            # order.receiver_address_book = db.query(AddressBookModel.address).filter(AddressBookModel.address_book_id == order.receiver_address_book_id).scalar()
            order.receiver_company_name = db.query(AddressBookModel.company_name).filter(AddressBookModel.address_book_id == order.receiver_address_book_id).scalar()
            
            # order.sender_address_book = db.query(AddressBookModel.address).filter(AddressBookModel.address_book_id == order.sender_address_book_id).scalar()
            order.sender_company_name = db.query(AddressBookModel.company_name).filter(AddressBookModel.address_book_id == order.sender_address_book_id).scalar()
            order.parcel_type_name = db.query(ParcelType.parcel_name).filter(ParcelType.parcel_id == order.parcel_type_id).scalar()
            order.shipment_status_name = db.query(ShipmentStatusModel.shipment_status_name).filter(ShipmentStatusModel.shipment_status_id == order.shipment_status_id).scalar()
            order.driver_name = db.query(DriverModel.name).filter(DriverModel.driver_id == order.driver_id).scalar()
            order.vehicle_name = db.query(VehicleModel.name).filter(VehicleModel.id == order.vehicle_id).scalar()
            order.display_docket = order.manual_docket if order.is_docket_auto else order.docket_no

            order.order_items = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.order_id).all()
            order.sender_address = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == order.sender_address_book_id).first()
            order.receiver_address = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == order.receiver_address_book_id).first()
            order.order_trackings = db.query(OrderTrackingModel).filter(OrderTrackingModel.order_id == order.order_id).first()


        return {
        "message": "Orders retrieved successfully",
        "total": len(orders_data),
        "orders": orders_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


def get_order_by_id(db: Session, order_id: int, current_user: User):
   
    get_order = db.query(OrderModel).filter(OrderModel.order_id == order_id, OrderModel.is_deleted == False).first()

    if not get_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    

     # Fetch the related order items (if any)
    order_item = db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id, OrderItemModel.is_active == True).all()
    sender_address = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == get_order.sender_address_book_id).first()
    receiver_address = db.query(AddressBookModel).filter(AddressBookModel.address_book_id == get_order.receiver_address_book_id).first()
    
    user_dict = {user.user_id: user.first_name for user in db.query(User).all()}
    get_order.created_by_name = user_dict.get(get_order.created_by, 'Unknown')
    get_order.updated_by_name = user_dict.get(get_order.updated_by, 'Unknown')
    get_order.order_item = order_item
    get_order.sender_address = sender_address
    get_order.receiver_address = receiver_address


    return {
        "message": "Order retrieved successfully",
        "order": get_order
    }

def create_order(db: Session, order_service_data: CreateOrderSchema, current_user: User):
    
    try:
            
            docket_no = None
            

       
            latest_order = db.query(OrderModel).order_by(OrderModel.docket_no.desc()).first()
            docket_no = 202100000 if not latest_order else latest_order.docket_no + 1

            # Check if docket_no should be auto-generated
            manual_docket = order_service_data.manual_docket if order_service_data.is_docket_auto else None
            
            # new_sender_address = None
            if order_service_data.sender_address:

                # address_book_dict = order_service_data.dict(exclude_unset=True)
                sender_address_book_id = None

                if order_service_data.sender_address_book_id and order_service_data.sender_address_book_id > 0:   #address_book_dict.get("sender_address_book_id"):
                        existing_sender_address =  db.query(AddressBookModel).filter_by(address_book_id=order_service_data.sender_address_book_id).first() #db.query(AddressBookModel).get(order_service_data.sender_address_book_id)

                        if  existing_sender_address:
                            sender_address_book_id = existing_sender_address.address_book_id
                            new_sender_address = existing_sender_address
                            
                    # else:
                    #     sender_address_book_id = None
                        
                if sender_address_book_id is None and order_service_data.sender_address:
                    # if not address_book_dict.get("sender_address_book_id"):
                        new_sender_address = AddressBookModel(**order_service_data.sender_address.dict())
                        db.add(new_sender_address)
                        db.commit()
                        db.refresh(new_sender_address)
                        sender_address_book_id = new_sender_address.address_book_id 

            # new_order.sender_address_book_id = sender_address_book_id 

            if order_service_data.receiver_address:
                receiver_address_book_id= None

                if order_service_data.receiver_address_book_id and order_service_data.receiver_address_book_id > 0:   #address_book_dict.get("sender_address_book_id"):
                        existing_receiver_address =  db.query(AddressBookModel).filter_by(address_book_id=order_service_data.receiver_address_book_id).first() #db.query(AddressBookModel).get(order_service_data.sender_address_book_id)

                        if  existing_receiver_address:
                            receiver_address_book_id = existing_receiver_address.address_book_id


                if receiver_address_book_id is None and order_service_data.receiver_address:
                    # if not address_book_dict.get("sender_address_book_id"):
                        new_receiver_address = AddressBookModel(**order_service_data.receiver_address.dict())
                        db.add(new_receiver_address)
                        db.commit()
                        db.refresh(new_receiver_address)
                        receiver_address_book_id = new_receiver_address.address_book_id 
            



            order_dict = order_service_data.dict(exclude={"order_items","sender_address","receiver_address","order_trackings"}, exclude_unset=True)
            order_dict["created_by"] = current_user.user_id
            order_dict["docket_no"] = docket_no
            order_dict["sender_address_book_id"] = sender_address_book_id
            order_dict["receiver_address_book_id"] = receiver_address_book_id
            order_dict["shipment_status_id"] = 1
            order_dict["manual_docket"] = manual_docket



            new_order = OrderModel(**order_dict)
            db.add(new_order)
            db.commit()
            
            db.refresh(new_order)
            
           

            order_items_list = []
            new_order_item = None

            if order_service_data.order_items:  # Assuming order_items are part of the request
                for order_item_data in order_service_data.order_items:
                    # for order_item_data in order_service_data.order_item:
                    # order_item_dict = order_item_data.dict(exclude_unset=True)
                    order_item_dict = order_item_data.dict(exclude_unset=True)
                    order_item_dict["created_by"] = current_user.user_id
                    order_item_dict["order_id"] = new_order.order_id  
                    
                    
                    # Create the new OrderItem and add it to the session
                    new_order_item = OrderItemModel(**order_item_dict)
                    db.add(new_order_item)
                    db.commit()
                    db.refresh(new_order_item)


                    # order_items_list.append(new_order_item)

                # Commit the order items to the database
                # db.commit()


                    order_items_list.append(
                        # new_order_item
                        GetOrderItemSchema.from_orm(new_order_item).dict() if new_order_item else None
                        # "order_item_id": new_order_item.order_item_id,
                        # "order_id": new_order_item.order_id,
                        # "number_of_box": new_order_item.number_of_box,
                        # "parcel_hight": new_order_item.parcel_hight,
                        # "parcel_width": new_order_item.parcel_width,
                        # "parcel_breadth": new_order_item.parcel_breadth,
                        # "volume": new_order_item.volume,
                        # "is_active": new_order_item.is_active
                    )


            if order_service_data.order_trackings:  # Assuming order_trackings are part of the request
                # for order_tracking_data  in order_service_data.order_trackings:

                    # order_tracking_dict = order_tracking_data.dict(exclude_unset=True)
                    order_tracking_dict = order_service_data.order_trackings.dict(exclude_unset=True)
                    order_tracking_dict["created_by"] = current_user.user_id
                    order_tracking_dict["order_id"] = new_order.order_id  
                    
                    new_order_tracking = OrderTrackingModel(**order_tracking_dict)
                    db.add(new_order_tracking)
                    db.commit()
                    db.refresh(new_order_tracking)


                   

            
            # Return the newly created order
            return {
                "message": "Order created successfully",            
                # "order": new_order
                "order": {
                    "order_id": new_order.order_id,
                    "docket_no": new_order.docket_no,
                    "manual_docket": new_order.manual_docket,
                    "payment_type": new_order.payment_type,
                    "cod_amount": new_order.cod_amount,
                    "service_type_id": new_order.service_type_id,
                    "payment_mode_id": new_order.payment_mode_id,
                    "customer_id": new_order.customer_id,
                    "gst_number": new_order.gst_number,
                    "receiver_address_book_id": new_order.receiver_address_book_id,
                    "sender_address_book_id": new_order.sender_address_book_id,

                    "parcel_type_id": new_order.parcel_type_id,
                    "shipment_value": new_order.shipment_value,
                    "invoice_no": new_order.invoice_no,
                    "e_way_bill": new_order.e_way_bill,
                    "forwarding": new_order.forwarding,
                    "booking_instruction": new_order.booking_instruction,
                    "is_active": new_order.is_active,
                    "created_by": new_order.created_by,
                    "total_box_size": new_order.total_box_size,
                    "total_no_of_box": new_order.total_no_of_box,
                    "dimension_type": new_order.dimension_type,
                    "total_volume": new_order.total_volume,
                    "parcel_weight": new_order.parcel_weight,
                    "is_fragile": new_order.is_fragile, 
                    "shipment_status_id":new_order.shipment_status_id,

                    "order_items": order_items_list,
                    "order_tracking": new_order_tracking,
                    # "sender_address":new_sender_address,
                    # "receiver_address": new_receiver_address,
                     
                }
            }
    
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating order: {str(e)}")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating order: {str(e)}")


def update_order(
    db: Session, order_id: int, update_order_service_data: UpdateOrderSchema, current_user: User
):
    try:
        # Fetch existing order
        order_update = db.query(OrderModel).filter(
            OrderModel.order_id == order_id, OrderModel.is_deleted == False
        ).first()

        if not order_update:
            raise HTTPException(status_code=404, detail="Order not found")

        
        if update_order_service_data.sender_address:

                # address_book_dict = order_service_data.dict(exclude_unset=True)
                sender_address_book_id = None

                if update_order_service_data.sender_address_book_id and update_order_service_data.sender_address_book_id > 0:   #address_book_dict.get("sender_address_book_id"):
                        existing_sender_address =  db.query(AddressBookModel).filter_by(address_book_id=update_order_service_data.sender_address_book_id).first() #db.query(AddressBookModel).get(order_service_data.sender_address_book_id)

                        if  existing_sender_address:
                            sender_address_book_id = existing_sender_address.address_book_id
                            new_sender_address = existing_sender_address
                            
                    # else:
                    #     sender_address_book_id = None
                        
                if sender_address_book_id is None and update_order_service_data.sender_address:
                    # if not address_book_dict.get("sender_address_book_id"):
                        new_sender_address = AddressBookModel(**update_order_service_data.sender_address.dict())
                        db.add(new_sender_address)
                        db.commit()
                        db.refresh(new_sender_address)
                        sender_address_book_id = new_sender_address.address_book_id 


        
        if update_order_service_data.receiver_address:
                receiver_address_book_id= None

                if update_order_service_data.receiver_address_book_id and update_order_service_data.receiver_address_book_id > 0:   #address_book_dict.get("sender_address_book_id"):
                        existing_receiver_address =  db.query(AddressBookModel).filter_by(address_book_id=update_order_service_data.receiver_address_book_id).first() #db.query(AddressBookModel).get(order_service_data.sender_address_book_id)

                        if  existing_receiver_address:
                            receiver_address_book_id = existing_receiver_address.address_book_id


                if receiver_address_book_id is None and update_order_service_data.receiver_address:
                    # if not address_book_dict.get("sender_address_book_id"):
                        new_receiver_address = AddressBookModel(**update_order_service_data.receiver_address.dict())
                        db.add(new_receiver_address)
                        db.commit()
                        db.refresh(new_receiver_address)
                        receiver_address_book_id = new_receiver_address.address_book_id 
        
        

        existing_order_items = {item.order_item_id: item for item in db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).all()}
        new_order_items = []

        for order_item_data in update_order_service_data.order_items or []:
            order_item_dict = order_item_data.dict(exclude_unset=True)
            order_item_id = order_item_dict.get("order_item_id")

            if order_item_id and order_item_id != 0 and order_item_id in existing_order_items:
                existing_item = existing_order_items[order_item_id]
                updated = False  # Track if any update is made

                for key, value in order_item_dict.items():
                    if key != "order_item_id" and getattr(existing_item, key) != value:
                        setattr(existing_item, key, value)
                        updated = True

                if updated:  # Commit changes only if an update occurred
                    existing_item.updated_by = current_user.user_id  # Track who updated it
                    db.add(existing_item)

            elif not order_item_id or order_item_id == 0:
                order_item_dict.pop("order_id", None)  # Prevent duplicate order_id assignment
                new_order_item = OrderItemModel(**order_item_dict)
                new_order_item.created_by = current_user.user_id
                new_order_item.order_id = order_update.order_id

                db.add(new_order_item)
                new_order_items.append(new_order_item)

        db.commit()



        if update_order_service_data.order_trackings:  
               
                    order_tracking_dict = update_order_service_data.order_trackings.dict(exclude_unset=True)
                    order_tracking_dict["created_by"] = current_user.user_id
                    order_tracking_dict["order_id"] = order_update.order_id  
                    
                    new_order_tracking = OrderTrackingModel(**order_tracking_dict)
                    db.add(new_order_tracking)
                    db.commit()
                    db.refresh(new_order_tracking)
        



        # Convert schema to dictionary and update only provided fields (exclude={"order_items","sender_address","receiver_address"}
        update_data = update_order_service_data.dict(exclude={"sender_address","receiver_address","order_items","order_trackings"}, exclude_unset=True)
        update_data["updated_by"] = current_user.user_id
        update_data["sender_address_book_id"] = sender_address_book_id
        update_data["receiver_address_book_id"] = receiver_address_book_id


        

        for key, value in update_data.items():

                if key == 'payment_type' and value:
                    value = PaymentTypeEnum(value)

                elif key == "dimension_type" and value:
                    value = DimensionTypeEnum(value)  
                setattr(order_update, key, value)

        # Commit changes to the database
        db.commit()
        db.refresh(order_update)

        return {
        "message": "Order updated successfully",
        "order": order_update,


    }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Error updating order: {str(e)}")

def assign_driver_to_order(db: Session, order_ids: List[int], assign_driver_vehicle : AssignDriverVehicleSchema, current_user: User):
        
    try:
        # order = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
        orders = db.query(OrderModel).filter(OrderModel.order_id.in_(order_ids)).all()
        driver = db.query(DriverModel).filter(DriverModel.driver_id == assign_driver_vehicle.driver_id).first()
        vehicle = db.query(VehicleModel).filter(VehicleModel.id == assign_driver_vehicle.vehicle_id).first()
        shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.is_deleted==False).all()

        shipment_status_name = "Pending Pickup"
        # matched_status = next((status for status in shipment_status if status.shipment_status_name.lower() == shipment_status_name.lower()), None)
        matched_status = next(
            (status for status in shipment_status if status.shipment_status_name.lower() == shipment_status_name.lower()), 
            None
        )

        if not orders:
            raise HTTPException(status_code=404, detail="Order not found")
        if not driver:
            raise HTTPException(status_code=400, detail="Driver not found")
        if not vehicle:
            raise HTTPException(status_code=400, detail="Vehicle not found")
        if not matched_status:
            raise HTTPException(status_code=404, detail=f"Shipment status '{shipment_status_name}' not found")
        
        created_order_trackings = []

        for order in orders:
            order.driver_id = driver.driver_id
            order.vehicle_id = vehicle.id
            order.shipment_status_id = matched_status.shipment_status_id
            order.updated_by = current_user.user_id
            order.appointment_date_time = assign_driver_vehicle.appointment_date_time
            db.add(order)


            if assign_driver_vehicle.order_trackings:  
               
                    order_tracking_dict = assign_driver_vehicle.order_trackings.dict(exclude_unset=True)
                    order_tracking_dict["created_by"] = current_user.user_id
                    order_tracking_dict["order_id"] = order.order_id  
                    
                    new_order_tracking = OrderTrackingModel(**order_tracking_dict)
                    db.add(new_order_tracking)
                    db.commit()
                    db.refresh(new_order_tracking)

                    created_order_trackings.append(new_order_tracking)

        
    
        db.commit()
        # db.refresh(order)
        return {"message": "Driver and Vehicle assigned successfully",
                "assigned_orders": [
                {"order_id": order.order_id, "shipment_status": matched_status.shipment_status_name, "appointment_date_time": order.appointment_date_time} for order in orders
            ],
            "order_trackings": [tracking.order_id for tracking in created_order_trackings]
        }
    
    except Exception as e:
        db.rollback()  # Rollback in case of an error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

def update_shipment_status(db: Session, order_id: int, update_shipment_status_data: UpdateShipmentStatusSchema, current_user: User):
    
    try:

        order_update = db.query(OrderModel).filter(
            OrderModel.order_id == order_id,
            OrderModel.is_deleted == False
        ).first()

        # shipment_status = db.query(ShipmentStatusModel).filter(ShipmentStatusModel.is_deleted==False).all()

        if not order_update:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Order not found or has been deleted"
            )

        update_data = update_shipment_status_data.dict(exclude_unset=True)
        update_data["updated_by"] = current_user.user_id
        # update_data.shipment_status_id = shipment_status.shipment_status_id

        new_order_tracking = None  # Initialize as None to avoid uninitialized variable issues
        
        if update_shipment_status_data.order_trackings:  
               
                    order_tracking_dict = update_shipment_status_data.order_trackings.dict(exclude_unset=True)
                    order_tracking_dict["created_by"] = current_user.user_id
                    order_tracking_dict["order_id"] = order_update.order_id  
                    
                    new_order_tracking = OrderTrackingModel(**order_tracking_dict)
                    db.add(new_order_tracking)
                    db.commit()
                    db.refresh(new_order_tracking)


        for key, value in update_data.items():
            
            setattr(order_update, key, value)
        # Update shipment status & comment if provided
        # if update_shipment_status_data.shipment_status_id is not None:
        #     order_update.shipment_status_id = update_shipment_status_data.shipment_status_id
        
        # if update_shipment_status_data.comment is not None:
        #     order_update.comment = update_shipment_status_data.comment

        # Commit changes
        db.commit()
        db.refresh(order_update)

        return {"message": "Shipment status updated successfully", "order_id": order_id, "order_trackings": GetOrderTrackingSchema.from_orm(new_order_tracking) if new_order_tracking else None}
         
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Error updating order: {str(e)}")
    

def confirm_pickup(db: Session, docket_no: int,current_user: User):
    try:
         # Fetch order using order_id
        order = db.query(OrderModel).filter(
            OrderModel.docket_no == docket_no, OrderModel.is_deleted == False
        ).first()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

       
       # Ensure order is in 'Pending Pickup' status
        pending_pickup_status = db.query(ShipmentStatusModel).filter(
            ShipmentStatusModel.shipment_status_name.ilike("Pending Pickup"),
            ShipmentStatusModel.is_deleted == False
        ).first()


        if not pending_pickup_status:
            raise HTTPException(status_code=404, detail="Shipment status not found")


        if order.shipment_status_id != pending_pickup_status.shipment_status_id:
            raise HTTPException(status_code=400, detail="Order is not in 'Pending Pickup' status")


        in_transit_status = db.query(ShipmentStatusModel).filter(
            ShipmentStatusModel.shipment_status_name.ilike("In Transit"),
            ShipmentStatusModel.is_deleted == False
        ).first()

        if not in_transit_status:
            raise HTTPException(status_code=404, detail="In Transit status not found")
        
        # Update order status to "InTransit"
        order.shipment_status_id = in_transit_status.shipment_status_id
        order.updated_by = current_user.user_id

        new_order_tracking = None

        # Create order tracking entry
        new_order_tracking = OrderTrackingModel(
            order_id=order.order_id,
            # status=in_transit_status.shipment_status_name,
            created_by=current_user.user_id
        )
        db.add(new_order_tracking)

        db.commit()
        db.refresh(order)
        db.refresh(new_order_tracking)


        return {
            "message": "Pickup confirmed and status updated to InTransit",
            "docket_no": docket_no,
            "order_id": order.order_id,
            "shipment_status": in_transit_status.shipment_status_name,
            "shipment_status_id": in_transit_status.shipment_status_id,
            "confirmed_by_user_id": current_user.user_id,
            "order_trackings":GetOrderTrackingSchema.from_orm(new_order_tracking) if new_order_tracking else None
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



def delete_order(db: Session, order_id: int,current_user: User):
   
    delete_order_data = db.query(OrderModel).filter(OrderModel.order_id == order_id, OrderModel.is_deleted == False).first()
    
    if not delete_order_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Order not found or already deleted"
            )
        
    db.query(OrderItemModel).filter(OrderItemModel.order_id == order_id).update({"is_deleted": True,"is_active": False}, synchronize_session=False)
    
    delete_order_data.is_deleted = True  # Mark as deleted (soft delete)
    delete_order_data.is_active = False


    new_order_tracking = None  # Initialize as None to avoid uninitialized variable issues
        
               
                     
    
    new_order_tracking = OrderTrackingModel(
            order_id=delete_order_data.order_id,
            created_by=current_user.user_id
        )
    db.add(new_order_tracking)
    db.commit()
    

    db.commit()  # Commit the changes
    db.refresh(delete_order_data)  # Refresh to update the state
    db.refresh(new_order_tracking)

    return delete_order_data


UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_pod_upload_file(file: UploadFile) -> str:
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return file_path


def update_pod_file(db: Session, order_id: int, file_path: str ,current_user: User):
    
    orderData = db.query(OrderModel).filter(OrderModel.order_id == order_id).first()
    if not orderData:
        return None  # Handle this in the router

    orderData.pod = file_path
    db.commit()
    return orderData




