from fastapi import *
from sqlalchemy.orm import Session
from datetime import *

from app.models.model import TimeSlot
from app.schemas.schemas import TimeSlotRequest
from app.services.database import get_db

router = APIRouter(prefix="/owner", tags=["Owner"])

@router.post("/set-timeslots")
def set_timeslots(data:TimeSlotRequest, db: Session=Depends(get_db)):
    opening = data.opening_time
    closing = data.closing_time
    lunch = data.lunch_time
    
    # clear old slots before setting new
    # db.query(TimeSlot).delete()
    
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