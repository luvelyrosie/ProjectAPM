from fastapi import APIRouter, Path, status
from ..dependencies import *
from ..models import Workstation


router=APIRouter(
    prefix="/workstations",
    tags=["workstations"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_workstations(db: db_dependency, user: user_dependency):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(Workstation).all()


@router.get("/{workstation_id}", status_code=status.HTTP_200_OK)
async def get_workstation_by_id(db: db_dependency, user: user_dependency,
                                workstation_id: int= Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    workstation_model=db.query(Workstation).filter(Workstation.id==workstation_id).first()
    
    if workstation_model is None:
        raise HTTPException(status_code=404, detail="The workstation not found")
    return workstation_model