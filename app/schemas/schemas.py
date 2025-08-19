from pydantic import BaseModel
from datetime import time


# For auth.py
class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: str
    
class UserLogin(BaseModel):
    email: str
    password: str


# For time_slots.py
class TimeSlotRequest(BaseModel):
    opening_time : time
    closing_time : time
    lunch_time : time


# For service.py
class ServiceBase(BaseModel):
    name : str
    cost : int

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

class ServiceOut(ServiceBase):
    id: int
    class Config:
        orm_mode = True
        

# For booking.py
class SlotRequest(BaseModel):
    id : int
    start_time : time
    end_time : time
    
class BookingsResponse(BaseModel):
    customer_id : int
    service_id : int
    booking_date : str
    time_slot_id : int
    cost : int
    