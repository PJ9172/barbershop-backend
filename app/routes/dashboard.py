from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.database import get_db
from app.models.model import Booking, ManualBooking

router = APIRouter(prefix="/owner", tags=["Owner Dashboard"])

@router.get("/get-total-income")
def get_total_income(db: Session = Depends(get_db)):
    # Online bookings
    online_income = db.query(func.coalesce(func.sum(Booking.cost), 0)).scalar()
    online_customers = db.query(func.count(func.distinct(Booking.customer_id))).scalar()

    # Manual bookings
    manual_income = db.query(func.coalesce(func.sum(ManualBooking.cost), 0)).scalar()
    manual_customers = db.query(func.count(ManualBooking.id)).scalar()

    # Combine results
    total_income = online_income + manual_income
    total_customers = online_customers + manual_customers

    return {
        "total_income": total_income,
        "total_customers": total_customers
    }
