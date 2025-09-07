import shutil
from fastapi import APIRouter, File, Form, Path, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from ..dependencies import *
from typing import List
from ..models import OrderFile
import os

router=APIRouter(
    prefix="/order_files",
    tags=["order files"]
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/order/{order_id}", response_model=List[dict])
async def get_order_files(db: db_dependency,user: user_dependency, 
                          order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    files = db.query(OrderFile).filter(OrderFile.order_id == order_id).all()
    return [{"id": f.id, "filename": f.filename, "filepath": f.filepath} for f in files]


@router.get("/file/{file_id}", response_class=FileResponse)
async def download_file(db: db_dependency, user: user_dependency, file_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    file = db.query(OrderFile).filter(OrderFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(path=file_path, filename=file.filename)


@router.get("/page/{order_id}/files", response_class=HTMLResponse)
async def order_files_page(request: Request, db: db_dependency, user: user_dependency_cookie, order_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Not authorized"})

    files = db.query(OrderFile).filter(OrderFile.order_id == order_id).all()

    return templates.TemplateResponse(
        "order_files.html",
        {"request": request, "files": files, "order_id": order_id, "user": user}
    )
    

@router.post("/create-order-file", status_code=status.HTTP_201_CREATED)
async def create_order_file(db: db_dependency,
                            user: user_dependency, order_id: int = Form(...), 
                            uploaded_file: UploadFile = File(...)
                            ):

    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    file_location = f"{UPLOAD_DIR}/{uploaded_file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    order_file = OrderFile(order_id=order_id, filename=uploaded_file.filename, filepath=file_location)
    db.add(order_file)
    db.commit()
    db.refresh(order_file)

    return {"id": order_file.id, "filename": order_file.filename, "filepath": order_file.filepath}


@router.put("/update-order-file/{file_id}", status_code=status.HTTP_200_OK)
async def update_order_file(db: db_dependency, user: user_dependency,
                            file_id: int = Path(gt=0),uploaded_file: UploadFile = File(...)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    file = db.query(OrderFile).filter(OrderFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    old_path = os.path.join(UPLOAD_DIR, file.filename)
    if os.path.exists(old_path):
        os.remove(old_path)

    new_path = os.path.join(UPLOAD_DIR, uploaded_file.filename)
    with open(new_path, "wb") as buffer:
        shutil.copyfileobj(uploaded_file.file, buffer)

    file.filename = uploaded_file.filename
    file.filepath = new_path
    db.commit()
    db.refresh(file)

    return {"id": file.id, "filename": file.filename, "filepath": file.filepath}


@router.delete("/delete-order-file/{file_id}", status_code=status.HTTP_200_OK)
async def delete_order_file(db : db_dependency, user: user_dependency, file_id: int = Path(gt=0)):
    if user is None or user.get("user_role") not in ["operator", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    file = db.query(OrderFile).filter(OrderFile.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if os.path.exists(file.filepath):
        os.remove(file.filepath)

    db.delete(file)
    db.commit()

    return JSONResponse(content={"detail": "File deleted successfully"})
