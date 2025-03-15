from datetime import datetime
from app.db.base import Base
from sqlalchemy import  Column, Integer,Float,Enum, String, Boolean,DateTime, ForeignKey,DefaultClause
import enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func




class PaymentTypeEnum(enum.Enum):
    CLIENT_PAYMENT = "CLIENT_PAYMENT"
    CASH_ON_DELIVERY = "CASH_ON_DELIVERY"

class DimensionTypeEnum(enum.Enum):
    CM = "CM"
    INCH = "INCH"
    FEET = "FEET"


class OrderModel(Base):
    __tablename__ = "order"

    order_id = Column(Integer,primary_key=True,index=True)
    docket_no = Column(Integer(),unique=True,index=True)
    manual_docket = Column(String(255), unique=True,nullable=True)
    
    total_box_size = Column(Integer ,nullable=True)
    total_no_of_box = Column(Integer ,nullable=True)

    dimension_type = Column (Enum(DimensionTypeEnum), nullable=True)
    total_volume = Column(Float, nullable= True)
    parcel_weight = Column(Integer, nullable=True)
    is_fragile = Column ( Boolean, default=False)
    appointment_date_time = Column(DateTime, nullable=True)
    comment = Column (String, nullable=True)

    payment_type = Column(Enum(PaymentTypeEnum), nullable=True)
    cod_amount = Column(Integer, nullable=True)
    service_type_id = Column(Integer, ForeignKey("service_type.service_id"))
    payment_mode_id = Column(Integer, ForeignKey("paymentModes.payment_id"))
    customer_id = Column(Integer, ForeignKey("users.user_id"))
    driver_id = Column(Integer, ForeignKey("drivers.driver_id"), nullable=True)
    vehicle_id = Column(Integer, ForeignKey("vehicle.id"), nullable=True)


    gst_number = Column(Integer, nullable=True)
    # address_book_id = Column(Integer, ForeignKey("address_book.address_book_id"))
    receiver_address_book_id = Column(Integer, ForeignKey("address_book.address_book_id"),nullable=True,default=None)
    sender_address_book_id = Column(Integer, ForeignKey("address_book.address_book_id"),nullable=True,default=None)

    parcel_type_id = Column(Integer, ForeignKey("parcel_type.parcel_id"))
    shipment_value = Column(Integer, nullable=True)
    invoice_no =Column(Integer,nullable=True)
    e_way_bill = Column(Integer, nullable=True)
    forwarding = Column(Integer, nullable=True)
    booking_instruction = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)

    is_docket_auto = Column(Boolean, default=False)
    shipment_status_id = Column(Integer, ForeignKey("shipment_status.shipment_status_id"),nullable=False)
    pod = Column(String, nullable=True)

    






    orderItems = relationship("OrderItemModel", back_populates="orders")
    # orderItems = relationship("OrderItemModel", back_populates="orders", cascade="all, delete-orphan")
    serviceTypes = relationship("ServiceType", back_populates="orders")
    payment_modes = relationship("PaymentMode", back_populates="orders")
    customers = relationship("User", back_populates="orders")
    # customers = relationship("User",foreign_keys=[customer_id], back_populates="orders")
    drivers = relationship("DriverModel", back_populates="orders")
    vehicles = relationship("VehicleModel", back_populates="orders")


    # addressBooks = relationship("AddressBookModel",back_populates="orders")
    receiver_address = relationship("AddressBookModel", foreign_keys=[receiver_address_book_id], back_populates="receiver_orders")
    sender_address = relationship("AddressBookModel", foreign_keys=[sender_address_book_id], back_populates="sender_orders")

    parcelTypes = relationship("ParcelType", back_populates="orders")
    shipmentStatus = relationship("ShipmentStatusModel", back_populates="orders")

    orderTrackings = relationship("OrderTrackingModel", back_populates="orders")




