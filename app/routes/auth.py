from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session 
from app.schemas.schemas import UserCreate     # Class to store db data of user
from app.schemas.schemas import UserLogin      # Class to store db data of login 
from app.schemas.schemas import TokenPair, RefreshIn, DeviceInfo
from app.models.model import User        # DB Schema of table
from app.services.database import get_db
from app.services.hash import hash_password, verify_password
from app.services.otp import *
from app.services.email import send_email
from app.schemas.schemas import UserLogin, TokenPair, RefreshIn, DeviceInfo
from app.services.token_service import mint_token_pair, rotate_refresh, revoke_refresh
from app.services.deps import get_current_user

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
    return {"success": True, "msg": "User created", "user_id":new_user.id}




@router.post("/login", response_model=TokenPair)
def login(body: UserLogin, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    device_id = getattr(body, "device_id", None) if hasattr(body, "device_id") else None
    ua = request.headers.get("user-agent")
    access, refresh = mint_token_pair(db, user, device_id=device_id, user_agent=ua)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


@router.post("/refresh", response_model=TokenPair)
def refresh_tokens(body: RefreshIn, request: Request, db: Session = Depends(get_db)):
    ua = request.headers.get("user-agent")
    access, new_refresh = rotate_refresh(db, body.refresh_token, user_agent=ua)
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer"}

@router.post("/logout")
def logout(body: RefreshIn, db: Session = Depends(get_db)):
    revoke_refresh(db, body.refresh_token)
    return {"success": True}

@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    # If you prefer, create a response model for User public fields
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "role": current_user.role,
    }