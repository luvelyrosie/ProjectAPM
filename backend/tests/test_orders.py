from fastapi import status, Request
from .utils import *
from app.main import app
from app.dependencies import get_db, get_current_user_from_cookie, get_current_user


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


async def fake_user_cookie(request: Request):
    return None


async def override_get_current_user_cookie(request: Request):
    return {
        "id": 1,
        "username": "admin_test",
        "email": "admin_test@abc.com",
        "user_role": "admin",
    }


def test_orders_page_redirect_if_not_logged_in():
    app.dependency_overrides[get_current_user_from_cookie] = fake_user_cookie

    response = client.get("/orders/page")
    assert response.status_code == 200
    assert "login" in response.text.lower()

    app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user_cookie


app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user_cookie


def test_orders_page_logged_in(test_user, test_order):
    response = client.get("/orders/page")
    assert response.status_code == status.HTTP_200_OK
    assert "orders" in response.text.lower()


def test_order_detail_page(test_user, test_order):
    response = client.get(f"/orders/page/{test_order.id}")
    assert response.status_code == status.HTTP_200_OK
    assert test_order.name in response.text


def test_order_files_page(test_user, test_order_file):
    response = client.get(f"/orders/page/{test_order_file.order_id}/files")
    assert response.status_code == status.HTTP_200_OK
    assert test_order_file.filename in response.text


def test_read_all_orders(test_user, test_order):
    response = client.get("/orders/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(o["id"] == test_order.id for o in data)


def test_get_order_by_id(test_user, test_order):
    response = client.get(f"/orders/{test_order.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_order.id


def test_get_order_tasks(test_user, test_task):
    response = client.get(f"/orders/{test_task.order_id}/tasks")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert isinstance(tasks, list)
    assert any(t["name"] == test_task.name for t in tasks)


def test_start_order_success(test_user, test_order, db):
    test_order.status = "Готово к работе"
    db.commit()
    db.refresh(test_order)

    response = client.post(f"/orders/{test_order.id}/start")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "В работе"


def test_start_order_invalid_status(test_user, test_order, db):
    test_order.status = "Готово"
    db.commit()
    db.refresh(test_order)

    response = client.post(f"/orders/{test_order.id}/start")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_complete_order_success(test_user, test_order, db):
    test_order.status = "В работе"
    db.commit()
    db.refresh(test_order)

    response = client.post(f"/orders/{test_order.id}/complete")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "Готово"


def test_complete_order_invalid_status(test_user, test_order, db):
    test_order.status = "Готово к работе"
    db.commit()
    db.refresh(test_order)

    response = client.post(f"/orders/{test_order.id}/complete")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_reject_order_success(test_user, test_order):
    data = {"description": "Defect in materials"}
    response = client.post(f"/orders/{test_order.id}/reject", json=data)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == "Брак"
    assert body["reject_reason"] == data["description"]


def test_reject_order_missing_reason(test_user, test_order):
    response = client.post(f"/orders/{test_order.id}/reject", json={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST