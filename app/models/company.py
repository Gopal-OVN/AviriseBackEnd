from sqlalchemy import BigInteger, Column, Integer, String, Text, Boolean, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    registration_number = Column(String(100), unique=True, nullable=False)
    gst_number = Column(String(15))
    pan_number = Column(String(10))
    logo = Column(String(255))  # Store file path or URL here
    address = Column(Text)
    contact_persons = Column(JSON, nullable=False)
    created_by = Column(Integer) 
    user_limit = Column(Integer)
    country_id = Column(Integer, ForeignKey("country.id"))
    state_id = Column(Integer, ForeignKey("state.id"))
    city_id = Column(Integer, ForeignKey("city.id"))
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Foreign Keys
    industry_type_id = Column(BigInteger, ForeignKey("industry_type.id"), nullable=True)
    globle_status_id = Column(Integer, ForeignKey("globle_status.id"), nullable=True)

    # Relationships with IndustryType and GlobleStatus
    industry_type = relationship("IndustryType", backref="company_industry", foreign_keys=[industry_type_id])
    globle_status = relationship("GlobleStatus", backref="company_status", foreign_keys=[globle_status_id])
    
    country = relationship("Country", backref="company_with_country", foreign_keys=[country_id])
    state = relationship("State", backref="company_with_state", foreign_keys=[state_id])
    city = relationship("City", backref="company_with_city", foreign_keys=[city_id])
    
    @property
    def country_name(self):
        return self.country.name if self.country else None

    @property
    def state_name(self):
        return self.state.name if self.state else None

    @property
    def city_name(self):
        return self.city.name if self.city else None

    

    
