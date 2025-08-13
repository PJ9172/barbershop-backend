from fastapi import *
from sqlalchemy.orm import Session
from app.models import booking
from app.services.database import get_db

router = APIRouter()

# @router.post("/confrim-booking")
# def confirm_booking(booking):
    