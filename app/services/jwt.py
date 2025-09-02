# app/services/jwt.py
import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "CHANGE_ME")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MIN = int(os.getenv("ACCESS_TOKEN_EXPIRE_MIN", "15"))

def create_access_token(sub: str, extra: Optional[Dict[str, Any]] = None,
                        minutes: Optional[int] = None) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=minutes or ACCESS_TOKEN_EXPIRE_MIN)
    payload: Dict[str, Any] = {"sub": sub, "exp": exp}
    if extra:
        payload.update(extra)  # e.g., {"role": "...", "name": "..."} if you want
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
