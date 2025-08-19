from fastapi import *
from sqlalchemy.orm import Session
from typing import List

from app.models.model import Booking
from app.models.model import TimeSlot
from app.services.database import get_db
from app.schemas.schemas import SlotRequest
from app.schemas.schemas import BookingsResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/slots{date}", response_model=List[SlotRequest])
def get_available_slots(date : str, db : Session = Depends(get_db)):
    slots = db.query(TimeSlot).all()
    
    available = []
    for s in slots:
        count = db.query(Booking).filter(
            Booking.booking_date == date,
            Booking.time_slot_id == s.id
        ).count()
        if count < 2:
            available.append(
                SlotRequest(
                    id = s.id,
                    start_time = s.start_time,
                    end_time = s.end_time,
                )
            )
    return available


@router.post("/confirm")
def confirm_booking(data : BookingsResponse, db : Session = Depends(get_db)):
    count = db.query(Booking).filter(
        Booking.booking_date == data.booking_date,
        Booking.time_slot_id == data.time_slot_id
    ).count()
    
    if count >= 2:
        raise HTTPException(status_code = 400, detail = "Slot already full!!!")
    
    new_booking = Booking(
        customer_id = data.customer_id,
        service_id = data.service_id,
        booking_date = data.booking_date,
        time_slot_id = data.time_slot_id,
        cost = data.cost
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return {"message" : "Booking Confirmed", "booking_id" : new_booking.id}