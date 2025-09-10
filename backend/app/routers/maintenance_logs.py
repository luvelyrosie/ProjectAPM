from fastapi import APIRouter, Path, status
from ..dependencies import *
from ..models import MaintenanceLog
from ..schemas import MaintenanceLogCreate, MaintenanceLogUpdate


router=APIRouter(
    prefix="/maintenance_logs",
    tags=["maintenance logs"]
)

@router.get("/", status_code=status.HTTP_200_OK)
async def read_logs(db: db_dependency, user: user_dependency):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db.query(MaintenanceLog).all()


@router.post("/create-logs", status_code=status.HTTP_201_CREATED)
async def create_logs(db: db_dependency, user: user_dependency,
                      log_request: MaintenanceLogCreate):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    log_model=MaintenanceLog(**log_request.model_dump())
    
    db.add(log_model)
    db.commit()
    db.refresh(log_model)
    return log_model


@router.get("/{log_id}", status_code=status.HTTP_200_OK)
async def read_log_by_id(db: db_dependency, user: user_dependency,
                         log_id: int= Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    log_model=db.query(MaintenanceLog).filter(MaintenanceLog.id==log_id).first()
    if log_model is None:
        raise HTTPException(status_code=404, detail="Maintenance log not found")
    
    return log_model


@router.put("/update-logs/{log_id}", status_code=status.HTTP_200_OK)
async def update_log(log_update: MaintenanceLogUpdate, user: user_dependency,
                     db: db_dependency, log_id: int= Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    log_model = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
    if not log_model:
        raise HTTPException(status_code=404, detail="Maintenance log not found")

    update_data = log_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(log_model, key, value)

    db.commit()
    db.refresh(log_model)
    return log_model