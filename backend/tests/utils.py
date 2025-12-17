import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.models import Base, User, Task, RejectReason, Order, Workstation, MaintenanceLog, Performance, OrderFile
from app.dependencies import bcrypt_context, get_db, get_current_user_from_cookie, get_current_user
from app.main import app
import tempfile
import os
import shutil

SQLALCHEMY_DATABASE_URL = "sqlite:///test_projectapm.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


async def override_get_current_user():
    """For bearer token/API authentication"""
    return {"id": 1, "username": "admin_test", "email": "admin_test@abc.com", "user_role": "admin"}


async def override_get_current_user_cookie(request):
    """For cookie-based page authentication"""
    return {"id": 1, "username": "admin_test", "email": "admin_test@abc.com", "user_role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user_cookie


client = TestClient(app)


@pytest.fixture
def db():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_user(db):
    user = User(
        username="admin_test",
        email="admin_test@abc.com",
        hashed_password=bcrypt_context.hash("test1234"),
        role="admin"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users;"))
        conn.commit()


@pytest.fixture
def test_order(db):
    order = Order(
        name="Test Order",
        status="Готово к работе",
        start_time=datetime.now(timezone.utc)
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    yield order
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM orders;"))
        conn.commit()


@pytest.fixture
def test_workstation(db):
    workstation = Workstation(
        name="Test Workstation",
        description="Workstation for testing"
    )
    db.add(workstation)
    db.commit()
    db.refresh(workstation)
    yield workstation
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM workstations;"))
        conn.commit()


@pytest.fixture
def test_reject_reason(db):
    reason = RejectReason(description="Test reject reason")
    db.add(reason)
    db.commit()
    db.refresh(reason)
    yield reason
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM reject_reasons;"))
        conn.commit()


@pytest.fixture
def test_task(db, test_order, test_workstation, test_user):
    task = Task(
        name="Test Task",
        order_id=test_order.id,
        workstation_id=test_workstation.id,
        operator_id=test_user.id,
        status="Готово к работе",
        start_time=datetime.now(timezone.utc)
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    yield task
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM tasks;"))
        conn.commit()


@pytest.fixture
def test_maintenance_log(db, test_workstation):
    log = MaintenanceLog(
        workstation_id=test_workstation.id,
        type="Repair",
        description="Replaced a broken part"
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    yield log
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM maintenance_logs;"))
        conn.commit()


@pytest.fixture
def test_performance(db, test_user, test_task):
    performance = Performance(
        user_id=test_user.id,
        task_id=test_task.id,
        points=5
    )
    db.add(performance)
    db.commit()
    db.refresh(performance)
    yield performance
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM performance;"))
        conn.commit()


@pytest.fixture
def test_order_file(db, test_order):
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, "test_document.pdf")
    with open(temp_file_path, "wb") as f:
        f.write(b"Test content")

    file = OrderFile(
        order_id=test_order.id,
        filename="test_document.pdf",
        filepath=temp_file_path
    )
    db.add(file)
    db.commit()
    db.refresh(file)
    yield file

    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
    shutil.rmtree(temp_dir)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM order_files;"))
        conn.commit()