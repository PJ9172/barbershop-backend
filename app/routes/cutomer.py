from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.services.database import get_db
from app.services.deps import get_current_user
from app.models.model import Booking, User, Service, TimeSlot
from app.schemas.schemas import UpdateCustomerRequest, BookingHistoryResponse

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.get("/get-bookings-history", response_model=List[BookingHistoryResponse])
def get_bookings_history(id: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    id = id["id"]
    bookings = (
        db.query(Booking)
        .join(Service, Booking.service_id == Service.id)
        .join(TimeSlot, Booking.time_slot_id == TimeSlot.id)
        .filter(Booking.customer_id == id)
        .order_by(Booking.id.desc())
        .all()
    )

    result = []
    for b in bookings:
        result.append({
            "id": b.id,
            "booking_date": b.booking_date,
            "created_at": b.created_at,
            "service_name": b.services.name,
            "service_cost": b.services.cost,
            "start_time": b.timeslots.start_time,
            "end_time": b.timeslots.end_time,
        })

    return result

@router.get("/get-customre-info")
def get_customer_info(id : int, db : Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == id).first()
    return customer

@router.put("/update-customer-profile")
def update_customer_profile(data : UpdateCustomerRequest, db : Session = Depends(get_db)):
    customer = db.query(User).filter(User.id == data.id).first()
    
    customer.name = data.name
    customer.email = data.email
    customer.phone = data.phone
    customer.password = data.password
    
    db.commit()
    db.refresh(customer)
    return {"success" : True, "message" : "Profile Updated", "Info" : customer}
