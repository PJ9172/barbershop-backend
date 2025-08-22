from fastapi import FastAPI
from app.routes import auth
from app.routes import otp
from app.routes import owner
from app.routes import service
from app.routes import booking
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(owner.router)
app.include_router(service.router)
app.include_router(booking.router)