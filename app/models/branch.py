from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.models.industry_type import IndustryType
from app.models.globle_status import GlobleStatus
from app.models.user import User


class Branch(Base):
    __tablename__ = 'branch'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    address = Column(Text)
    contact_number = Column(String(10))
    contact_persons = Column(JSON)
    email = Column(String(255))
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    globle_status_id = Column(Integer, ForeignKey('globle_status.id'), default=1)

    created_by = Column(Integer)
    updated_by = Column(Integer)
    country_id = Column(Integer, ForeignKey("country.id"))
    state_id = Column(Integer, ForeignKey("state.id"))
    city_id = Column(Integer, ForeignKey("city.id"))    
    logo = Column(String(255)) 
    is_deleted = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationship with GlobleStatus
    status = relationship("GlobleStatus", backref="branches", foreign_keys=[globle_status_id])
    country = relationship("Country", backref="branches_with_country", foreign_keys=[country_id])
    state = relationship("State", backref="branches_with_state", foreign_keys=[state_id])
    city = relationship("City", backref="branches_with_city", foreign_keys=[city_id])

    @property
    def country_name(self):
        return self.country.name if self.country else None

    @property
    def state_name(self):
        return self.state.name if self.state else None

    @property
    def city_name(self):
        return self.city.name if self.city else None

    
    @property
    def status_name(self):
        return self.status.name if self.status else None

