from pydantic import BaseModel
from datetime import time, date


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


# For owner.py
class TimeSlotRequest(BaseModel):
    opening_time : time
    closing_time : time
    lunch_time : time

class EmergencyHolidayRequest(BaseModel):
    emergency_date : date
    details : str

class ManualBookingRequest(BaseModel):
    name : str
    phone : str
    service_id : int
    cost : int

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
    
class BookingsCreate(BaseModel):
    customer_id : int
    service_id : int
    booking_date : date
    time_slot_id : int
    cost : int
    
# For customer.py
class UpdateCustomerRequest(BaseModel):
    id : int
    name : str
    email : str
    phone : str
    password : str
