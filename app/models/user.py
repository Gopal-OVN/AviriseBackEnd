from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.db.base import Base
# from app.models.vehicle import VehicleModel

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)  # Primary key
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255))
    license_no = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone_number = Column(String(20))
    address = Column(Text)
    country_id = Column(Integer, ForeignKey("country.id"))
    state_id = Column(Integer, ForeignKey("state.id"))
    city_id = Column(Integer, ForeignKey("city.id"))
    pincode = Column(String(10))
    created_at = Column(DateTime, default=func.now())  # Automatically set when created
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())  # Automatically update when modified
    last_login = Column(DateTime, nullable=True) 
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"))  # Foreign key reference to Role model
    branch_id = Column(Integer, ForeignKey("branch.id"), nullable=True)  # Foreign key to Branch table
    company_id = Column(Integer, ForeignKey("company.id"), nullable=True)  # Foreign key to Company table
    status_id = Column(Integer, ForeignKey("globle_status.id"), nullable=True)


    # Relationships
    role = relationship("Role", backref="users_with_role", foreign_keys=[role_id])
    branch = relationship("Branch", backref="users_with_branch", foreign_keys=[branch_id])
    company = relationship("Company", backref="users_with_company", foreign_keys=[company_id])
    country = relationship("Country", backref="users_with_country", foreign_keys=[country_id])
    state = relationship("State", backref="users_with_state", foreign_keys=[state_id])
    city = relationship("City", backref="users_with_city", foreign_keys=[city_id])
    status = relationship("GlobleStatus", backref="users", foreign_keys=[status_id])
    # addresses = relationship("AddressBookModel", back_populates="users")

    orders = relationship("OrderModel",back_populates="customers")
    # orders = relationship("OrderModel", foreign_keys="[OrderModel.customer_id]", back_populates="customers")

    # orders = relationship("OrderModel",back_populates="drivers")




    # Corrected relationship for drivers
    drivers = relationship("DriverModel", back_populates="user")


    @property
    def role_name(self):
        return self.role.role_name if self.role else None

    @property
    def branch_name(self):
        return self.branch.name if self.branch else None

    @property
    def company_name(self):
        return self.company.name if self.company else None
    
    @property
    def city_name(self):
        if self.city:
            return self.city.name
        return None

    @property
    def state_name(self):
        if self.state:
            return self.state.name
        return None

    @property
    def country_name(self):
        if self.country:
            return self.country.name
        return None

    def update_last_login(self):
        """Updates last login time."""
        self.last_login = datetime.now()
