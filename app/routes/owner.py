from fastapi import *
from sqlalchemy.orm import Session
from datetime import *

from app.models.model import TimeSlot, WeekHoliday, EmergencyHoliday
from app.schemas.schemas import TimeSlotRequest, EmergencyHolidayRequest
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
    return {"message" : "Time-Slots generated successfully"}


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
    return {"message" : "Week Holiday Set", "index_of_day" : new_holiday.index}


@router.post("/set-emergency-holiday")
def set_emergency_holiday(data : EmergencyHolidayRequest, db : Session = Depends(get_db)):
    if data.emergency_date > date.today():
        new_data = EmergencyHoliday(
            emergency_date = data.emergency_date,
            details = data.details
        )
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        return {"message" : "Emergency Holiday Date added..."}
    else:
        raise HTTPException(status_code=404, detail="Past dates are not allowed...")