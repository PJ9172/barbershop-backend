import random
from datetime import datetime, timedelta
from app.utils.send_otp_sms import send_otp_sms

otp_store = {}      #in-memory store

def generate_otp():
    return str(random.randint(100000,999999))

def save_otp(phone, otp):
    expiry_time = datetime.now() + timedelta(minutes=5)
    otp_store[phone] = {"otp":otp, "expiry_time":expiry_time}
    
def validate_otp(phone, otp):
    record = otp_store.get(phone)
    if not record:
        return False
    if datetime.now() > record["expiry_time"]:
        return False
    if record["otp"] == otp:
        del otp_store[phone]
        return True
    return False

