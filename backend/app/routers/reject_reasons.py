from fastapi import APIRouter, Path, status
from ..dependencies import *
from ..models import RejectReason


router=APIRouter(
    prefix="/reject_reasons", 
    tags=["reject reasons"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_reject_reasons(db: db_dependency, user: user_dependency):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    return db.query(RejectReason).all()


@router.get("/{reason_id}", status_code=status.HTTP_200_OK)
async def get_reject_reason_by_id(db: db_dependency, user: user_dependency,
                                  reason_id: int= Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    reason_model=db.query(RejectReason).filter(RejectReason.id==reason_id).first()
    
    if reason_model is None:
        raise HTTPException(status_code=404, detail="The reject reason not found")
    
    return reason_model