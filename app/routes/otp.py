from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.otp import *

router = APIRouter()

class VerifyOTP(BaseModel):
    phone : str
    otp : str
    
class SendOTP(BaseModel):
    phone : str
    
@router.post("/verify-otp")
def verify_otp(data:VerifyOTP):
    if validate_otp(data.phone, data.otp):
        return {"success": True, "message": "OTP verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
@router.post("/send-otp")
def send_otp(data:SendOTP):
    otp=generate_otp()
    save_otp(phone=data.phone, otp=otp)
    if send_otp_sms(phone=data.phone, otp=otp):
        return {"msg" : "OTP send successfully.."}
    else:
        return {"msg" : "Error to send OTP"}