from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.services.database import get_db
from app.services.email import send_email
from app.services.hash import *
from app.services.deps import get_current_user, require_roles
from app.models.model import Booking, User
from app.schemas.schemas import UpdateCustomerRequest

router = APIRouter(prefix="/customer", tags=["Customer"], dependencies=[Depends(require_roles("customer"))])

@router.get("/get-bookings-history")
def get_bookings_history(id: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    id = id["id"]
    bookings = db.query(Booking).filter(Booking.customer_id == id, Booking.payment_status == "done").all()
    response = []
    for b in bookings:
        response.append({
            "id" : b.id,
            "service_name" : b.services.name,
            "service_cost" : b.cost,
            "booking_date" : b.booking_date,
            "start_time" : b.timeslots.start_time,
            "end_time" : b.timeslots.end_time,
            "payment_status" : b.payment_status
        })
    return response

@router.get("/get-upcoming-bookings")
def get_upcoming_bookings(id: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    id = id["id"]
    today = date.today()
    bookings = db.query(Booking).filter(Booking.customer_id == id, Booking.booking_date >= today, Booking.payment_status != "cancel").all()
    response = []
    for b in bookings:
        response.append({
            "id" : b.id,
            "service_name" : b.services.name,
            "service_cost" : b.cost,
            "booking_date" : b.booking_date,
            "start_time" : b.timeslots.start_time,
            "end_time" : b.timeslots.end_time,
            "payment_status" : b.payment_status
        })
    return response

@router.get("/get-cancellable-bookings")
def get_cancellable_bookings(id: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    id = id["id"]
    today = date.today()
    bookings = db.query(Booking).filter(Booking.customer_id == id, Booking.booking_date > today, Booking.payment_status == "pending").all()
    response = []
    for b in bookings:
        response.append({
            "id" : b.id,
            "service_name" : b.services.name,
            "service_cost" : b.cost,
            "booking_date" : b.booking_date,
            "start_time" : b.timeslots.start_time,
            "end_time" : b.timeslots.end_time,
            "payment_status" : b.payment_status
        })
    return response

@router.get("/get-customre-info")
def get_customer_info(id : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    id = id["id"]
    customer = db.query(User).filter(User.id == id).first()
    return customer

@router.put("/update-customer-profile")
def update_customer_profile(data : UpdateCustomerRequest, id : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    id = id["id"]
    customer = db.query(User).filter(User.id == id).first()
    customer.name = data.name
    if customer.email != data.email:
        customer.email = data.email
        send_email(data.email, data.name)
    customer.phone = data.phone
    if data.password : 
        customer.password = hash_password(data.password)
    
    db.commit()
    db.refresh(customer)
    return {"success" : True, "message" : "Profile Updated", "Info" : customer}

@router.post("/verify-password")
def verify_pass(password: str, db : Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid Credentials")
    return {"success" : True, "message" : "Valid Password"}
