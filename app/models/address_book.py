from app.db.base import Base
from sqlalchemy import  Column, Integer, String, Boolean,DateTime, ForeignKey,DefaultClause
from datetime import datetime
from sqlalchemy.orm import relationship


class AddressBookModel(Base):
    __tablename__ = 'address_book'

    address_book_id = Column(Integer, primary_key=True,index=True)
    # customer_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    company_name = Column(String(255),  nullable=True)
    contact_name = Column(String(255),  nullable=True)
    # name = Column(String(255),  nullable=True, unique=False,)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(20),nullable=True)
    
    address = Column(String, nullable=True)

    country_id = Column(Integer,ForeignKey("country.id"),default=1 ,nullable=True)
    state_id = Column(Integer, ForeignKey("state.id"), nullable=True)
    city_id = Column(Integer, ForeignKey("city.id"), nullable=True)
    
    pincode = Column(String(10),nullable=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(Integer)
    updated_by = Column(Integer) 
    is_manual_generate = Column ( Boolean, default=False)
    

    # Define relationships
    state = relationship("State", back_populates="addresses")
    city = relationship("City", back_populates="addresses")
    # users = relationship("User",back_populates="addresses")
    countries = relationship("Country",back_populates="addresses")
    # orders = relationship("OrderModel",back_populates="addressBooks")
    receiver_orders = relationship("OrderModel", foreign_keys="[OrderModel.receiver_address_book_id]", back_populates="receiver_address")
    sender_orders = relationship("OrderModel", foreign_keys="[OrderModel.sender_address_book_id]", back_populates="sender_address")






    
