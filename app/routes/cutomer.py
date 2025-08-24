from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.database import get_db
from app.models.model import Booking, User
from app.schemas.schemas import UpdateCustomerRequest

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.get("/get-bookings-history")
def get_bookings_history(id : int, db : Session = Depends(get_db)):
    bookings = (
    db.query(Booking)
    .filter(Booking.customer_id == id)
    .order_by(Booking.id.desc())   # or Booking.booking_date.desc()
    .all()
)
    return bookings

@router.get("/get-customre-info")
def get_customer_info(id : int, db : Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == id).first()
    return customer

@router.post("/update-customer-profile")
def update_customer_profile(data : UpdateCustomerRequest, db : Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == data.id).first()
    
    customer.name = data.name
    customer.email = data.email
    customer.phone = data.phone
    customer.password = data.password
    
    db.commit()
    db.refresh(customer)
    return {"success" : True      , "message" : "Profile Updated", "Info" : customer}
