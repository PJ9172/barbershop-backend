from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    booking_date = Column(Date, nullable=False)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"))
    cost = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    customers = relationship("User", back_populates="bookings")
    services = relationship("Service", back_populates="bookings")
    time_slots = relationship("TimeSlot", back_populates="bookings")
    
