from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.database import get_db
from app.models.model import Booking, ManualBooking

router = APIRouter(prefix="/owner", tags=["Owner Dashboard"])

@router.get("/get-total-income")
def get_total_income(
    filter: str = Query("all", description="Options: all, today, week, month"),
    db: Session = Depends(get_db)
):
    today = date.today()

    # Base queries
    booking_query = db.query(Booking)
    manual_booking_query = db.query(ManualBooking)

    # Apply filter
    if filter == "today":
        booking_query = booking_query.filter(Booking.booking_date == today)
        manual_booking_query = manual_booking_query.filter(
            func.date(ManualBooking.created_at) == today
        )
    elif filter == "week":
         # Start from Monday → Sunday
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        booking_query = booking_query.filter(Booking.booking_date.between(start_week, end_week))
        manual_booking_query = manual_booking_query.filter(
            func.date(ManualBooking.created_at).between(start_week, end_week)
        )
    elif filter == "month":
        start_month = today.replace(day=1)
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        end_month = next_month - timedelta(days=1)
        booking_query = booking_query.filter(Booking.booking_date.between(start_month, end_month))
        manual_booking_query = manual_booking_query.filter(
            func.date(ManualBooking.created_at).between(start_month, end_month)
        )
        
    # else "all" → no filter applied
    # Calculate totals
    total_income = sum(b.cost for b in booking_query.all()) + \
                   sum(m.cost for m in manual_booking_query.all())

    total_customers = booking_query.count() + manual_booking_query.count()

    return {
        "filter": filter,
        "total_income": total_income,
        "total_customers": total_customers
    }