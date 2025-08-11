from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session 
from app.schemas.user import UserCreate     # Class to store db data of user
from app.models.model import User        # DB Schema of table
from app.services.database import get_db
from app.services.hash import hash_password
from app.services.hash import verify_password
from app.services.otp import *
from app.schemas.user import UserLogin      # Class to store db data of login 
from app.services.email import send_email

router = APIRouter()
        
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_data = user.dict()         # Convert to Dictonary
    user_data["password"] = hash_password(user.password)
    
    new_user = User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    send_email(user.email, user.name)
    return {"msg": "User created", "user_id":new_user.id}




@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email==user.email).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password") 
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or passowrd")
    
    return {"msg": "Login Successful", "user_id": db_user.id, "role": db_user.role}