import os
import tempfile
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.models import Base, OrderFile, User, Order
from app.dependencies import get_db, get_current_user
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_projectapm.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {"id": 1, "username": "admin_test", "email": "admin@abc.com", "user_role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)


@pytest.fixture
def db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_order(db):
    order = Order(name="Test Order", status="Готово к работе")
    db.add(order)
    db.commit()
    db.refresh(order)
    yield order
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM orders;"))
        conn.commit()


@pytest.fixture
def test_order_file(db, test_order):
    UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, "test_document.pdf")
    with open(file_path, "wb") as f:
        f.write(b"Hello World!")

    file = OrderFile(order_id=test_order.id, filename="test_document.pdf", filepath=file_path)
    db.add(file)
    db.commit()
    db.refresh(file)
    yield file

    if os.path.exists(file_path):
        os.remove(file_path)
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM order_files;"))
        conn.commit()


# --- Tests ---
def test_create_order_file(test_order):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Test content")
        tmp.seek(0)
        response = client.post(
            "/order_files/create-order-file",
            data={"order_id": test_order.id},
            files={"uploaded_file": ("upload.pdf", tmp, "application/pdf")}
        )
    os.remove(tmp.name)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["filename"] == "upload.pdf"
    assert "id" in data


def test_get_order_files(test_order_file):
    response = client.get(f"/order_files/order/{test_order_file.order_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(f["id"] == test_order_file.id for f in data)


def test_download_file(test_order_file):
    response = client.get(f"/order_files/file/{test_order_file.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b"Hello World!"


def test_update_order_file(test_order_file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(b"Updated content")
        tmp.seek(0)
        response = client.put(
            f"/order_files/update-order-file/{test_order_file.id}",
            files={"uploaded_file": ("updated.pdf", tmp, "application/pdf")}
        )
    os.remove(tmp.name)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["filename"] == "updated.pdf"


def test_delete_order_file(test_order_file):
    response = client.delete(f"/order_files/delete-order-file/{test_order_file.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "File deleted successfully"


def test_unauthorized_access(monkeypatch, test_order_file):
    def fake_user():
        return {"id": 2, "username": "guest", "user_role": "guest"}

    app.dependency_overrides[get_current_user] = fake_user
    resp = client.get(f"/order_files/order/{test_order_file.order_id}")
    assert resp.status_code == status.HTTP_403_FORBIDDEN
    assert "not authorized" in resp.json()["detail"].lower()

    app.dependency_overrides[get_current_user] = override_get_current_user