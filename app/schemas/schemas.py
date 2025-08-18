from pydantic import BaseModel
from datetime import time

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str
    password: str
    role: str
    
class UserLogin(BaseModel):
    email: str
    password: str


class TimeSlotRequest(BaseModel):
    opening_time : time
    closing_time : time
    lunch_time : time
    
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