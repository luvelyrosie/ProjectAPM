from fastapi import APIRouter, Form, HTTPException, Path
from starlette import status
from fastapi.responses import HTMLResponse
from sqlalchemy import func
from ..dependencies import *
from ..schemas import *
from ..models import *

router=APIRouter(
    prefix="/admin",
    tags=["admin"]
)


# users
@router.get("/users", status_code=status.HTTP_201_CREATED)
async def read_all_users(db: db_dependency, user: user_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    return db.query(User).all()

 
@router.put("/users/update_user/{user_id}", status_code=status.HTTP_200_OK)
async def update_user_info(user_update: UserUpdate,db: db_dependency,
                           user: user_dependency, user_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    user_model = db.query(User).filter(User.id == user_id).first()
    if not user_model:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username is not None:
        user_model.username = user_update.username
    if user_update.email is not None:
        user_model.email = user_update.email
    if user_update.role is not None:
        user_model.role = user_update.role
        
    if user_update.password and user_update.new_password:
        if not bcrypt_context.verify(user_update.password, user_model.hashed_password):
            raise HTTPException(status_code=401, detail="Current password incorrect")
        user_model.hashed_password = bcrypt_context.hash(user_update.new_password)

    db.commit()
    db.refresh(user_model)
    return user_model


@router.delete("/users/delete-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_by_id(user: user_dependency, db: db_dependency,
                            user_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model=db.query(User).filter(User.id==user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="The user not found")
    db.query(User).filter(User.id==user_id).delete()
    db.commit()
    
    
# orders
@router.get("/orders/create-order-page", response_class=HTMLResponse)
async def create_order_page(request: Request, user: user_dependency_cookie):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return templates.TemplateResponse("create_order.html", {"request": request})


@router.post("/orders/create-order")
async def create_order_form(
    db: db_dependency,
    user: user_dependency_cookie,
    name: str = Form(...),
    status: str = Form(...)
):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")

    order_model = Order(
        name=name,
        status=status
    )
    db.add(order_model)
    db.commit()
    db.refresh(order_model)

    response = RedirectResponse(url="/orders/page", status_code=302)
    return response


@router.post("/orders/api/create-order", status_code=status.HTTP_201_CREATED)
async def create_order(db: db_dependency, user: user_dependency, order_request: OrderCreate):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    order_model=Order(**order_request.model_dump())
    
    db.add(order_model)
    db.commit()
    db.refresh(order_model)
    return order_model


@router.put("/orders/update-order/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_order_by_id(db: db_dependency, user: user_dependency,
                             order_update: OrderUpdate, order_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    order_model=db.query(Order).filter(Order.id==order_id).first()
    
    if order_model is None:
        raise HTTPException(status_code=404, detail="The order not found")
    
    if order_update.name is not None:
        order_model.name=order_update.name
    if order_update.status is not None:
        order_model.status=order_update.status
    if order_update.start_time is not None:
        order_model.start_time=order_update.start_time
    if order_update.end_time is not None:
        order_model.end_time=order_update.end_time
        
    db.commit()
    db.refresh(order_model)
    return order_model


@router.delete("/orders/delete-order/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order_by_id(db: db_dependency, user: user_dependency, order_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    order_model=db.query(Order).filter(Order.id==order_id).first()
    
    if order_model is None:
        raise HTTPException(status_code=404, detail="The order not found")
    
    db.query(Order).filter(Order.id==order_id).delete()
    db.commit()
    

# tasks
@router.post("/tasks/api/create-task", status_code=status.HTTP_201_CREATED)
async def create_task(db: db_dependency, user: user_dependency, task_request: TaskCreate):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    task_model=Task(**task_request.model_dump())
    
    db.add(task_model)
    db.commit()
    db.refresh(task_model)
    return task_model


@router.get("/tasks/create-task/page/{order_id}")
async def create_task_page(request: Request, order_id: int, user: user_dependency_cookie):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return templates.TemplateResponse("create_task.html", {"request": request, "order_id": order_id})



@router.post("/tasks/create-task")
async def create_task_form(db: db_dependency,user: user_dependency_cookie,
                           order_id: int = Form(...),name: str = Form(...),status: str = Form(...)):
    if user is None or user.get("user_role") != "admin":
        raise HTTPException(status_code=401, detail="Authentication Failed")

    task_model = Task(
        order_id=order_id,
        name=name,
        status=status
    )
    db.add(task_model)
    db.commit()
    db.refresh(task_model)

    response = RedirectResponse(url=f"/orders/page/{order_id}",status_code=302)
    return response


@router.delete("/delete-task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_by_id(db: db_dependency, user: user_dependency, task_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    task_model=db.query(Task.id==task_id).first()
    
    if task_model is None:
        raise HTTPException(status_code=404, detail="The task not found")
    
    db.query(Task).filter(Task.id==task_id).delete()
    db.commit()
    
    
# workstations
@router.post("/workstations/create-worksation", status_code=status.HTTP_201_CREATED)
async def create_workstation(db: db_dependency, user: user_dependency, workstation_request: WorkstationCreate):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    workstation_model=Workstation(**workstation_request.model_dump())
    
    db.add(workstation_model)
    db.commit()
    db.refresh(workstation_model)
    return workstation_model


@router.put("/workstations/update-workstation/{workstation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_workstation_by_id(db: db_dependency, user: user_dependency,
                                   workstation_update: WorkstationUpdate, workstation_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    workstation_model=db.query(Workstation).filter(Workstation.id==workstation_id).first()
    
    if workstation_model is None:
        raise HTTPException(status_code=404, detail="The workstation not found")
    
    update_data=workstation_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(workstation_model, key, value)
        
    db.commit()
    db.refresh(workstation_model)
    return workstation_model


@router.delete("/workstations/delete-workstation/{workstation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workstation_by_id(db: db_dependency, user: user_dependency, 
                                   workstation_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    workstation_model=db.query(Workstation.id==workstation_id).first()
    
    if workstation_model is None:
        raise HTTPException(status_code=404, detail="The workstation not found")
    
    db.query(Workstation).filter(Workstation.id==workstation_id).delete()
    db.commit()
    
    
# reject reasons
@router.post("/create-reject_reasons", status_code=status.HTTP_201_CREATED)
async def create_reject_reasons(db: db_dependency, user: user_dependency,
                                reason_request: RejectReasonCreate):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    reason_model=RejectReason(**reason_request.model_dump())
    
    db.add(reason_model)
    db.commit()
    db.refresh(reason_model)
    return reason_model


@router.put("/update-reject_reasons/{reason_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_reject_reason_by_id(db: db_dependency, user: user_dependency,
                                     reason_update: RejectReasonUpdate, reason_id: int= Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    reason_model=db.query(RejectReason).filter(RejectReason.id==reason_id).first()
    
    if reason_model is None:
        raise HTTPException(status_code=404, detail="The reject reason not found")
    
    update_data=reason_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reason_model, key, value)
        
    db.commit()
    db.refresh(reason_model)
    return reason_model


@router.delete("/delete-reject_reason/{reason_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_reject_reason_by_id(db: db_dependency, user: user_dependency,
                                     reason_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    reason_model=db.query(RejectReason.id==reason_id).first()
    
    if reason_model is None:
        raise HTTPException(status_code=404, detail="The reject reason not found")
    
    db.query(RejectReason).filter(RejectReason.id==reason_id).delete()
    db.commit()
    
    
# logs
@router.delete("/delete-log/{log_id}", status_code=204)
async def delete_log(db: db_dependency, user: user_dependency, log_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    log_model = db.query(MaintenanceLog).filter(MaintenanceLog.id == log_id).first()
    if not log_model:
        raise HTTPException(status_code=404, detail="Maintenance log not found")

    db.delete(log_model)
    db.commit()
    
    
# performance
@router.get("/performance/", status_code=status.HTTP_200_OK)
async def read_performance(db: db_dependency, user: user_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    return db.query(Performance).all()


@router.delete("/delete-performance/{perf_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_performance_by_id(db: db_dependency, user: user_dependency,
                                   perf_id: int=Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')

    perf_model=db.query(Performance.id==perf_id).first()
    
    if not perf_model:
        raise HTTPException(status_code=404, detail="The performance not found")
    
    db.query(Performance).filter(Performance.id==perf_id).delete()
    db.commit()
    
    
@router.get("/performance/by_user/{user_id}")
async def get_performance_by_user(db: db_dependency,user: user_dependency,
                                  user_id: int = Path(gt=0),):
    if user is None or user.get('user_role') != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    total_points = db.query(func.sum(Performance.points)).filter(Performance.user_id == user_id)\
                     .scalar() or 0
                     
    entries = db.query(Performance).filter(Performance.user_id == user_id).all()

    return {
        "user_id": user_id,
        "total_points": total_points,
        "entries": [
            {
                "task_id": e.task_id,
                "points": e.points,
                "created_at": e.created_at
            }
            for e in entries
        ]
    }