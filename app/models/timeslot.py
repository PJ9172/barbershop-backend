from sqlalchemy import *
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class TimeSlot(Base):
    __tablename__ = "timeslots"
    
    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    bookings = relationship("Booking", back_populates="timeslots")