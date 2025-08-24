from fastapi import FastAPI
from app.routes import auth, otp, owner, service, booking, cutomer
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth.router)
app.include_router(otp.router)
app.include_router(cutomer.router)
app.include_router(owner.router)
app.include_router(service.router)
app.include_router(booking.router)