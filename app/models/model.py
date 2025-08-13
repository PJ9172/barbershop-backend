from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


########################## User Model ######################
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "customer" or "owner"

    # Relationship for customer bookings
    bookings = relationship("Booking", back_populates="users")
    
    
######################### TimeSlot Model #######################
class TimeSlot(Base):
    __tablename__ = "timeslots"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    bookings = relationship("Booking", back_populates="timeslots")
    

######################## Service Model ###############################
class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    cost = Column(Integer, nullable=False)
    
    bookings = relationship("Booking", back_populates="services")
    
    
######################### Booking Model ##############################
class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    booking_date = Column(Date, nullable=False)
    time_slot_id = Column(Integer, ForeignKey("timeslots.id"))
    cost = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    users = relationship("User", back_populates="bookings")
    services = relationship("Service", back_populates="bookings")
    timeslots = relationship("TimeSlot", back_populates="bookings")