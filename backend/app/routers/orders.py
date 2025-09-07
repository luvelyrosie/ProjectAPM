from fastapi import APIRouter, Path, status
from typing import List

from fastapi.responses import FileResponse, HTMLResponse
from ..dependencies import *
from ..models import Order, Task, OrderFile
from ..schemas import TaskBase


router=APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_orders(db:db_dependency, user: user_dependency):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return db.query(Order).all()


@router.get("/page", response_class=HTMLResponse)
async def tasks_page(request: Request, db: db_dependency):
    user = await get_current_user_from_cookie(request)
    if not user:
        return redirect_to_login()

    orders = db.query(Order).all()
    return templates.TemplateResponse("orders.html", {"request": request, "orders": orders, "user": user})


@router.get("/page/{order_id}", response_class=HTMLResponse)
async def get_order_detail_page(request: Request,db: db_dependency,
                                user: user_dependency_cookie,order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Not authorized"}
        )

    order_model = db.query(Order).filter(Order.id == order_id).first()
    if order_model is None:
        return templates.TemplateResponse(
            "404.html", 
            {"request": request, "message": "Order not found"}
        )

    return templates.TemplateResponse(
        "order_detail.html",
        {"request": request, "order": order_model, "user": user}
    )


@router.get("/{order_id}", status_code=status.HTTP_200_OK)
async def get_order_by_id(db: db_dependency, user: user_dependency,
                          order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    order_model = db.query(Order).filter(Order.id == order_id).first()

    if order_model is None:
        raise HTTPException(status_code=404, detail="The order not found")

    return order_model


@router.get("/page/{order_id}/files", response_class=HTMLResponse)
async def get_order_files_page(request: Request,db: db_dependency,
                               user: user_dependency_cookie,order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Not authorized"}
        )

    order_model = db.query(Order).filter(Order.id == order_id).first()
    if not order_model:
        return templates.TemplateResponse(
            "404.html",
            {"request": request, "message": "Order not found"}
        )

    files = order_model.files

    return templates.TemplateResponse(
        "order_files.html",
        {"request": request, "order": order_model, "files": files, "user": user}
    )
    
    
@router.get("/{order_id}/tasks", status_code=status.HTTP_200_OK, response_model=List[TaskBase])
async def get_order_tasks(db: db_dependency, user: user_dependency, order_id: int= Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    tasks_model= db.query(Task).filter(Task.order_id == order_id).all()
    if tasks_model is None:
        raise HTTPException(status_code=404, detail="No tasks found for this order")
    return tasks_model


from fastapi import APIRouter, Depends, Path, Body, HTTPException, status
from datetime import datetime, timezone
from ..dependencies import db_dependency, user_dependency_cookie
from ..models import Order, RejectReason
from typing import Dict

# Start Order
@router.post("/{order_id}/start")
async def start_order(db: db_dependency, user: user_dependency_cookie, order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    order_model = db.query(Order).filter(Order.id == order_id).first()
    if not order_model:
        raise HTTPException(status_code=404, detail="Order not found")

    if order_model.status != "Готово к работе":
        raise HTTPException(status_code=400, detail="Order is not ready to start")

    order_model.status = "В работе"
    order_model.start_time = datetime.now(timezone.utc)

    db.commit()
    db.refresh(order_model)
    return {"message": "Order started", "order_id": order_model.id, "status": order_model.status}


# Complete Order
@router.post("/{order_id}/complete")
async def complete_order(db: db_dependency, user: user_dependency_cookie, order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    order_model = db.query(Order).filter(Order.id == order_id).first()
    if not order_model:
        raise HTTPException(status_code=404, detail="Order not found")

    if order_model.status != "В работе":
        raise HTTPException(status_code=400, detail="Order must be in progress before completion")

    order_model.status = "Готово"
    order_model.end_time = datetime.now(timezone.utc)

    db.commit()
    db.refresh(order_model)
    return {
        "message": "Order completed",
        "order_id": order_model.id,
        "status": order_model.status,
        "end_time": order_model.end_time
    }


# Reject Order
@router.post("/{order_id}/reject")
async def reject_order(db: db_dependency, user: user_dependency_cookie,
                       order_id: int = Path(gt=0), body: Dict = Body(...)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    reason_text = body.get("description")
    if not reason_text:
        raise HTTPException(status_code=400, detail="Reject reason is required")

    # Create RejectReason
    reject_reason = RejectReason(description=reason_text)
    db.add(reject_reason)
    db.commit()
    db.refresh(reject_reason)

    # Update Order
    order_model = db.query(Order).filter(Order.id == order_id).first()
    if not order_model:
        raise HTTPException(status_code=404, detail="Order not found")

    order_model.status = "Брак"
    order_model.end_time = datetime.now(timezone.utc)
    db.commit()
    db.refresh(order_model)

    return {
        "message": "Order rejected",
        "order_id": order_model.id,
        "status": order_model.status,
        "reject_reason": reject_reason.description,
    }