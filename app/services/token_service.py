# app/services/token_service.py
import os, secrets, hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.model import RefreshToken, User
from app.services.jwt import create_access_token

REFRESH_TOKEN_PEPPER = os.getenv("REFRESH_TOKEN_PEPPER", "PEPPER")
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "45"))

def _hash_refresh(raw: str) -> str:
    return hashlib.sha256((raw + REFRESH_TOKEN_PEPPER).encode()).hexdigest()

def _expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

def mint_token_pair(db: Session, user: User, device_id: str | None, user_agent: str | None):
    # raw refresh token to return to client
    raw_refresh = secrets.token_urlsafe(48)
    rt = RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh(raw_refresh),
        device_id=device_id,
        user_agent=user_agent,
        expires_at=_expiry(),
    )
    db.add(rt); db.commit(); db.refresh(rt)

    access = create_access_token(str(user.id), extra={"role": user.role, "name": user.name})
    return access, raw_refresh

def _get_valid_rt(db: Session, raw_refresh: str) -> RefreshToken:
    rt = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_refresh(raw_refresh)).first()
    if not rt or rt.revoked or rt.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return rt

def rotate_refresh(db: Session, raw_refresh: str, user_agent: str | None):
    old = _get_valid_rt(db, raw_refresh)
    user = db.query(User).filter(User.id == old.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # rotate: revoke old and mint new
    new_raw = secrets.token_urlsafe(48)
    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh(new_raw),
        device_id=old.device_id,
        user_agent=user_agent or old.user_agent,
        expires_at=_expiry(),
    )
    db.add(new_rt)
    old.revoked = True
    old.replaced_by = new_rt
    old.last_used_at = datetime.now(timezone.utc)
    db.commit(); db.refresh(new_rt)

    access = create_access_token(str(user.id), extra={"role": user.role, "name": user.name})
    return access, new_raw

def revoke_refresh(db: Session, raw_refresh: str):
    try:
        rt = _get_valid_rt(db, raw_refresh)
    except HTTPException:
        # already invalid → treat as logged out
        return
    rt.revoked = True
    rt.last_used_at = datetime.now(timezone.utc)
    db.commit()
