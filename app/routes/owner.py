from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import *

from app.models.model import TimeSlot, WeekHoliday, EmergencyHoliday, ManualBooking
from app.schemas.schemas import TimeSlotRequest, EmergencyHolidayRequest, ManualBookingRequest
from app.services.database import get_db

router = APIRouter(prefix="/owner", tags=["Owner"])

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
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
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