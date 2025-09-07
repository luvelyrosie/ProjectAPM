from fastapi import APIRouter, Body, Path, Query, status
from fastapi.responses import HTMLResponse
from ..dependencies import *
from ..models import Task, RejectReason, Performance
from ..schemas import TaskUpdate, RejectTaskBody
from fastapi.templating import Jinja2Templates


router=APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_tasks(db: db_dependency, user: user_dependency):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return db.query(Task).all()


@router.get("/")
async def get_tasks(db: db_dependency, user: user_dependency):
    tasks = db.query(Task).all()
    result = []
    for t in tasks:
        result.append({
            "id": t.id,
            "name": t.name,
            "order_id": t.order_id,
            "order_name": t.order.name if t.order else "",
            "status": t.status
        })
    return result


@router.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_task_by_id(db: db_dependency, user: user_dependency,
                         task_id: int= Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    task_model=db.query(Task).filter(Task.id==task_id).first()
    
    if task_model is None:
        raise HTTPException(status_code=404, detail="The task not found")
    return task_model


@router.put("/update-taks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_task_by_id(db: db_dependency,user: user_dependency,
                            task_update: TaskUpdate, task_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    task_model=db.query(Task).filter(Task.id==task_id).first()
    
    if task_model is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    update_data=task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task_model, key, value)
        
    db.commit()
    db.refresh(task_model)
    return task_model


@router.get("/by_operator/{user_id}", status_code=status.HTTP_200_OK)
async def get_tasks_by_operator(db: db_dependency, user: user_dependency, 
                                user_id: int=Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tasks = db.query(Task).filter(Task.operator_id == user_id).all()
    if not tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found for operator {user_id}")
    return tasks


# start task
@router.post("/{task_id}/start")
async def start_task(db: db_dependency, user: user_dependency_cookie, 
                     task_id: int=Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    task_model = db.query(Task).filter(Task.id == task_id).first()
    if not task_model:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_model.status != "Готово к работе":
        raise HTTPException(status_code=400, detail="Task is not ready to start")

    task_model.status = "В работе"
    task_model.start_time = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task_model)
    return {"message": "Task started", "task_id": task_model.id, "status": task_model.status}


# complete task
@router.post("/{task_id}/complete")
async def complete_task(db: db_dependency, user: user_dependency_cookie, task_id: int=Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    task_model = db.query(Task).filter(Task.id == task_id).first()
    if not task_model:
        raise HTTPException(status_code=404, detail="Task not found")

    if task_model.status != "В работе":
        raise HTTPException(status_code=400, detail="Task must be in progress before completion")

    task_model.status = "Готово"
    task_model.end_time = datetime.now(timezone.utc)
    
    perf = Performance(
        user_id=task_model.operator_id,
        task_id=task_model.id,
        points=1
    )
    db.add(perf)

    db.commit()
    db.refresh(task_model)
    return {
        "message": "Task completed",
        "Operator_id": task_model.operator_id, 
        "task_id": task_model.id,
        "status": task_model.status,
        "end_time": task_model.end_time
        }


# reject task
@router.post("/{task_id}/reject")
async def reject_task(db: db_dependency, user: user_dependency_cookie,
                      task_id: int = Path(gt=0), body: dict = Body(...)):

    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    reason_text = body.get("description")
    if not reason_text:
        raise HTTPException(status_code=400, detail="Reject reason is required")

    reject_reason = RejectReason(description=reason_text)
    db.add(reject_reason)
    db.commit()
    db.refresh(reject_reason)

    task_model = db.query(Task).filter(Task.id == task_id).first()
    if not task_model:
        raise HTTPException(status_code=404, detail="Task not found")

    task_model.status = "Брак"
    task_model.reject_reason_id = reject_reason.id
    task_model.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task_model)

    return {
        "message": "Task rejected",
        "task_id": task_model.id,
        "status": task_model.status,
        "reject_reason": reject_reason.description,
    }
