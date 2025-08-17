from fastapi import *
from sqlalchemy import Session
from typing import List

from app.services.database import get_db
from app.schemas.schemas import Services
from app.models.model import Service

router = APIRouter()

