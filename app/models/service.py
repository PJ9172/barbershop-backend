from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    
    bookings = relationship("Booking", back_populates="services")