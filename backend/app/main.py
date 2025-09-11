from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import users, orders, tasks, workstations, reject_reasons, maintenance_logs, performance, admin, order_files
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette import status
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware import ProxyHeadersMiddleware


app=FastAPI()

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


Base.metadata.create_all(bind=engine)


templates = Jinja2Templates(directory="frontend/templates")

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")


@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message":"The APM app is running"}


app.include_router(users.router)
app.include_router(orders.router)
app.include_router(tasks.router)
app.include_router(workstations.router)
app.include_router(reject_reasons.router)
app.include_router(maintenance_logs.router)
app.include_router(performance.router)
app.include_router(admin.router)
app.include_router(order_files.router)