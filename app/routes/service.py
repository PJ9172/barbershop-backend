from fastapi import *
from sqlalchemy.orm import Session
from typing import List

from app.services.database import get_db
from app.services.deps import require_roles
from app.schemas.schemas import *
from app.models.model import Service

router = APIRouter(prefix="/services", tags=["Services"], dependencies=[Depends(require_roles("owner"))])

# Get all services..
@router.get("/", response_model=List[ServiceOut])
def get_services(db : Session = Depends(get_db)):
    return db.query(Service).all()

# Add new Service....
@router.post("/add", response_model=ServiceOut)
def add_service(data : ServiceCreate, db : Session = Depends(get_db)):
    new_service = Service(name=data.name, cost = data.cost)
    db.add(new_service)
    db.commit()
    db.refresh(new_service)
    return new_service

# Update existing Service....
@router.put("/update/{id}", response_model=ServiceOut)
def update_service(id : int, data : ServiceUpdate, db : Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found!!!")
    
    service.name = data.name
    service.cost = data.cost
    db.commit()
    db.refresh(service)
    return service


# Delete existing Service...
@router.delete("/delete/{id}")
def delete_service(id : int, db : Session = Depends(get_db)):
    service = db.query(Service).filter(Service.id == id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found!!!")
    
    db.delete(service)
    db.commit()
    return {"message" : "Service Deleted Successfully"}