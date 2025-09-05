from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import *

from app.models.model import TimeSlot, WeekHoliday, EmergencyHoliday, ManualBooking, Booking, SlotCapacity
from app.schemas.schemas import TimeSlotRequest, EmergencyHolidayRequest, ManualBookingRequest
from app.services.database import get_db
from app.services.deps import require_roles

router = APIRouter(prefix="/owner", tags=["Owner"], dependencies=[Depends(require_roles("owner"))])

@router.post("/set-timeslots")
def set_timeslots(data:TimeSlotRequest, db: Session=Depends(get_db)):
    opening = data.opening_time
    closing = data.closing_time
    lunch = data.lunch_time
    
    # clear old slots before setting new
    count = db.query(TimeSlot).count()
    if count > 0:
        db.query(TimeSlot).delete()
    
    current_start = opening
    while current_start < closing:
        current_end = (datetime.combine(datetime.today(), current_start) + timedelta(hours=1)).time()
        print("current_start : ",current_start," and current_end",current_end)
        
        if current_start != lunch:
            slot = TimeSlot(start_time=current_start, end_time=current_end)
            db.add(slot)
        
        current_start = current_end
    
    db.commit()
    return {"success" : "True", "message" : "Time-Slots generated successfully"}


@router.post("/set-week-holiday")
def set_week_holiday(day : str, db : Session = Depends(get_db)):
    day = day.lower()
    weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if day in weekday_names:
        new_index = weekday_names.index(day)
    else:
        # raise HTTPException(status_code=404, detail="Invalid Day")
        new_index = None
        
    # clear old weekday holiday before setting new one
    count = db.query(WeekHoliday).count()
    if count > 0:
        db.query(WeekHoliday).delete()
        
    new_holiday = WeekHoliday(
        index = new_index
    )
    db.add(new_holiday)
    db.commit()
    db.refresh(new_holiday)
    return {"success": True, "message": "Week Holiday Set", "holiday": new_holiday.index}

@router.get("/get-week-holiday")
def get_week_holiday(db : Session = Depends(get_db)):
    holiday = db.query(WeekHoliday).first()
    if not holiday:
        return {"holiday" : None}
    weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return {"holiday" : weekday_names[holiday.index]}

@router.post("/set-slot-capacity")
def set_slot_capacity(capacity : int, db : Session = Depends(get_db)):
    if capacity <= 0:
        raise HTTPException(status_code=400, detail="Capacity must be greater than zero")
    
    # clear old slot capacity before setting new one
    count = db.query(SlotCapacity).count()
    if count > 0:
        db.query(SlotCapacity).delete()
        
    new_capacity = SlotCapacity(
        capacity = capacity
    )
    db.add(new_capacity)
    db.commit()
    db.refresh(new_capacity)
    return {"success": True, "message": "Slot Capacity Set", "capacity": new_capacity.capacity}

@router.get("/get-slot-capacity")
def get_slot_capacity(db : Session = Depends(get_db)):
    capacity = db.query(SlotCapacity).first()
    if not capacity:
        return {"capacity" : None}
    return {"capacity" : capacity.capacity}

@router.post("/set-emergency-holiday")
def set_emergency_holiday(data : EmergencyHolidayRequest, db : Session = Depends(get_db)):
    if data.emergency_date > date.today():
        # check already exists or not
        exists = db.query(EmergencyHoliday).filter(EmergencyHoliday.emergency_date == data.emergency_date).first()
        if exists:
            raise HTTPException(status_code=400, detail="Holiday already exists for this date")

        new_data = EmergencyHoliday(
            emergency_date = data.emergency_date,
            details = data.details
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        return {"success" : "True", "message" : "Emergency Holiday Date added..."}
    else:
        raise HTTPException(status_code=404, detail="Past dates are not allowed...")
    
@router.get("/get-emergency-holidays")
def get_emergency_holidays(db : Session = Depends(get_db)):
    dates = db.query(EmergencyHoliday).all()
    return dates

@router.post("/manual-bookings")
def manual_bookings(data : ManualBookingRequest, db : Session = Depends(get_db)):
    new_data = ManualBooking(
        name = data.name,
        phone = data.phone,
        service_id = data.service_id,
        cost = data.cost
    )
    db.add(new_data)
    db.commit()
    db.refresh(new_data)
    return {"success" : True, "message" : "Record added..", "customer" : new_data}

@router.get("/get-manual-bookings")
def get_manual_bookings(db : Session = Depends(get_db)):
    bookings = db.query(ManualBooking).all()
    response = []
    for b in bookings:
        response.append({
            "id": b.id,
            "name": b.name,
            "phone": b.phone,
            "service_name": b.services.name,
            "cost": b.cost,
            "created_at": b.created_at
        })
    return response

@router.post("/confirm-payment/{booking_id}")
def confirm_payment(booking_id : int, db : Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.payment_status == "done":
        raise HTTPException(status_code=400, detail="Payment already confirmed")
    
    booking.payment_status = "done"
    db.commit()
    db.refresh(booking)
    return {"success" : True, "message" : "Payment confirmed", "booking" : booking}

@router.post("/cancel-booking/{booking_id}")
def cancel_booking(booking_id : int, db : Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.payment_status == "cancel":
        raise HTTPException(status_code=400, detail="Booking already cancelled")
    
    booking.payment_status = "cancel"
    db.commit()
    db.refresh(booking)
    return {"success" : True, "message" : "Booking cancelled", "booking" : booking}

@router.get("/cancelled-bookings")
def cancelled_bookings(db : Session = Depends(get_db)):
    bookings = db.query(Booking).filter(Booking.payment_status == "cancel").all()
    response = []
    for b in bookings:
        response.append({
            "id": b.id,
            "customer_name": b.users.name,
            "service_name": b.services.name,
            "booking_date": b.booking_date,
            "time_slot": f"{b.timeslots.start_time} - {b.timeslots.end_time}",
            "cost": b.cost,
            "created_at": b.created_at
        })
    return response