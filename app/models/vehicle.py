from app.db.base import Base
from sqlalchemy import Date, Column, Integer, String, Boolean,DateTime ,Enum
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
import enum


# Define Enum class for vehicle type
class VehicleTypeEnum(enum.Enum):
    CAR = "CAR"
    BIKE = "BIKE"
    TRUCK = "TRUCK"
    BUS = "BUS"
    VAN = "VAN"


class VehicleModel(Base):
    __tablename__ = 'vehicle'

    id = Column(Integer, primary_key=True,index=True)
    name = Column(String,unique=True, nullable=False)
    vehicle_number = Column(String, unique=True, nullable=False)
    insurance_validity = Column(Date)
    rc_validity = Column(Date) #(Registration Certificate)
    # vehicle_type = Column(Enum('CAR', 'BIKE', 'TRUCK', 'BUS', 'VAN', name='vehicletypeenum'))
    vehicle_type = Column(Enum(VehicleTypeEnum), nullable=False)  # Using Enum for vehicle type
    # driver_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer)


    # users = relationship("User",back_populates="vehicles")
    orders = relationship("OrderModel", back_populates="vehicles")


