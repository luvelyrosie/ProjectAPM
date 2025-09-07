from fastapi import APIRouter, Path, status
from ..dependencies import *
from ..models import Performance
from ..schemas import PerformanceCreate, PerformanceUpdate


router=APIRouter(
    prefix="/performance",
    tags=["performance"]
)


@router.post("/create-performance/",status_code=status.HTTP_201_CREATED)
async def create_performance(perf_request: PerformanceCreate, user: user_dependency,
                             db: db_dependency):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    perf_model = Performance(**perf_request.model_dump())
    
    db.add(perf_model)
    db.commit()
    db.refresh(perf_model)
    return perf_model


@router.get("/performance/{perf_id}", status_code=status.HTTP_200_OK)
async def get_performance(db: db_dependency, user: user_dependency,
                          perf_id: int=Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    perf_model = db.query(Performance).filter(Performance.id == perf_id).first()
    if not perf_model:
        raise HTTPException(status_code=404, detail="Performance entry not found")
    return perf_model


@router.put("/performance/{perf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_performance(db: db_dependency, user: user_dependency,
                             perf_update: PerformanceUpdate, perf_id: int=Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    perf_model = db.query(Performance).filter(Performance.id == perf_id).first()
    if not perf_model:
        raise HTTPException(status_code=404, detail="Performance entry not found")

    update_data = perf_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(perf_model, key, value)

    db.commit()
    db.refresh(perf_model)
    return perf_model