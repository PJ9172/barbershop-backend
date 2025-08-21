from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timedelta

from app.models.model import *
from app.services.database import get_db
from app.schemas.schemas import *

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# 1. Get list of services
@router.get("/services", response_model=List[ServiceOut])
def get_services(db: Session = Depends(get_db)):
    services = db.query(Service).all()
    return services



# 2. Get available dates (exclude past dates)
@router.get("/available-dates")
def get_available_dates(db: Session = Depends(get_db)):
    today = datetime.now().date()
    dates = []

    for i in range(0, 15): 
        next_date = today + timedelta(days=i)
        dates.append(next_date.isoformat())

    return {"available_dates": dates}


# 3. Get available slots for a date
@router.get("/available-slots/{booking_date}", response_model=List[SlotRequest])
def get_available_slots(booking_date: date, db: Session = Depends(get_db)):
    slots = db.query(TimeSlot).all()
    available = []

    today = date.today()
    current_time = datetime.now().time()

    for s in slots:
        # filter only future slots if the date is today
        if booking_date == today and s.start_time <= current_time:
            continue

        count = db.query(Booking).filter(
            Booking.booking_date == booking_date,
            Booking.time_slot_id == s.id
        ).count()

        if count < 2:
            available.append(
                SlotRequest(
                    id=s.id,
                    start_time=s.start_time,
                    end_time=s.end_time,
                )
            )

    return available


@router.post("/confirm")
def confirm_booking(data: BookingsCreate, db: Session = Depends(get_db)):
    # extra validation: prevent booking past slots
    if data.booking_date < date.today():
        raise HTTPException(status_code=400, detail="Cannot book for past dates")

    if data.booking_date == date.today():
        current_time = datetime.now().time()
        slot = db.query(TimeSlot).filter(TimeSlot.id == data.time_slot_id).first()
        if slot and slot.start_time <= current_time:
            raise HTTPException(status_code=400, detail="Cannot book past time slot")

    count = db.query(Booking).filter(
        Booking.booking_date == data.booking_date,
        Booking.time_slot_id == data.time_slot_id
    ).count()

    if count >= 2:
        raise HTTPException(status_code=400, detail="Slot already full!!!")

    new_booking = Booking(
        customer_id=data.customer_id,
        service_id=data.service_id,
        booking_date=data.booking_date,
        time_slot_id=data.time_slot_id,
        cost=data.cost
    )

    try:
        db.add(new_booking)
        db.commit()
        db.refresh(new_booking)
    except:
        db.rollback()
        raise

    return {"message": "Booking Confirmed", "booking_id": new_booking.id}
