from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.database import get_db
from app.services.deps import require_roles
from app.models.model import Booking, ManualBooking, Service, User

router = APIRouter(prefix="/owner", tags=["Owner Dashboard"], dependencies=[Depends(require_roles("Owner"))])

@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    # Base queries
    booking_query = db.query(Booking)
    manual_booking_query = db.query(ManualBooking)

    total_income = sum(b.cost for b in booking_query.all()) + \
                sum(m.cost for m in manual_booking_query.all())    
    total_bookings = booking_query.count() + manual_booking_query.count() or 0
    total_services = db.query(func.count(Service.id)).scalar() or 0

    return {
        "total_income": total_income,
        "total_bookings": total_bookings,
        "services_offered": total_services
    }


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


@router.get("/gete-popular-services")
def popular_services(db: Session = Depends(get_db)):
    result = (
        db.query(
            Service.name.label("service_name"),
            func.count(Booking.id).label("total_bookings"),
            func.coalesce(func.sum(Booking.cost), 0).label("total_income")
        )
        .outerjoin(Booking, Booking.service_id == Service.id)
        .group_by(Service.id)
        .order_by(func.count(Booking.id).desc())
        .all()
    )

    # Convert SQLAlchemy Row objects into plain dicts
    response = [
        {
            "service_name": row.service_name,
            "total_bookings": row.total_bookings,
            "total_income": row.total_income
        }
        for row in result
    ]

    return response

# @router.get("/get-active-customers")
# def get_active_customers(db: Session = Depends(get_db)):
#     results = (
#         db.query(
#             User.name,
#             func.count(Booking.id).label("bookings"),
#             func.sum(Service.cost).label("total_spent")
#         )
#         .join(Booking, User.id == Booking.customer_id)
#         .join(Service, Booking.service_id == Service.id)
#         .group_by(User.id)
#         .order_by(func.count(Booking.id).desc())
#         .limit(5)
#         .all()
#     )

#     return [
#         {"customer_name": r[0], "bookings": r[1], "total_spent": r[2]}
#         for r in results
#     ]

@router.get("/get-total-customers")
def get_total_customers(db: Session = Depends(get_db)):
    online = db.query(User).filter(User.role == "customer").count()
    manual = db.query(ManualBooking).distinct(ManualBooking.phone).count()
    return {"total_customers": online+manual, "online_customers": online, "manual_customers": manual}