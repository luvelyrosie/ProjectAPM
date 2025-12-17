from .utils import *
from fastapi import status


def test_read_all_users(test_user):
    response = client.get("/admin/users")
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert any(u["id"] == test_user.id for u in data)


def test_update_user_info(test_user, db):
    payload = {"username": "new_admin", "email": "new_admin@abc.com", "role": "admin"}
    response = client.put(f"/admin/users/update_user/{test_user.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    updated = response.json()
    assert updated["username"] == payload["username"]
    assert updated["email"] == payload["email"]


def test_delete_user(test_user):
    response = client.delete(f"/admin/users/delete-user/{test_user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_order_api(test_order):
    payload = {"name": "API Order", "status": "Готово к работе"}
    response = client.post("/admin/orders/api/create-order", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]


def test_update_order_by_id(test_order):
    payload = {"name": "Updated Order", "status": "В работе"}
    response = client.put(f"/admin/orders/update-order/{test_order.id}", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_order_by_id(test_order):
    response = client.delete(f"/admin/orders/delete-order/{test_order.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_task_api(test_task):
    payload = {"name": "API Task", "order_id": test_task.order_id, "workstation_id": test_task.workstation_id,
               "operator_id": test_task.operator_id, "status": "Готово к работе"}
    response = client.post("/admin/tasks/api/create-task", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]


def test_delete_task_by_id(test_task):
    response = client.delete(f"/admin/delete-task/{test_task.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_workstation(test_workstation):
    payload = {"name": "API WS", "description": "Workstation API"}
    response = client.post("/admin/workstations/create-worksation", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == payload["name"]


def test_update_workstation_by_id(test_workstation):
    payload = {"name": "Updated WS", "description": "Updated description"}
    response = client.put(f"/admin/workstations/update-workstation/{test_workstation.id}", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_workstation_by_id(test_workstation):
    response = client.delete(f"/admin/workstations/delete-workstation/{test_workstation.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_create_reject_reasons(test_reject_reason):
    payload = {"description": "API Reject Reason"}
    response = client.post("/admin/create-reject_reasons", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["description"] == payload["description"]


def test_update_reject_reason_by_id(test_reject_reason):
    payload = {"description": "Updated Reason"}
    response = client.put(f"/admin/update-reject_reasons/{test_reject_reason.id}", json=payload)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_reject_reason_by_id(test_reject_reason):
    response = client.delete(f"/admin/delete-reject_reason/{test_reject_reason.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_log(test_maintenance_log):
    response = client.delete(f"/admin/delete-log/{test_maintenance_log.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_read_performance(test_performance):
    response = client.get("/admin/performance/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert any(p["id"] == test_performance.id for p in data)


def test_delete_performance_by_id(test_performance):
    response = client.delete(f"/admin/delete-performance/{test_performance.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_performance_by_user(test_user, test_performance):
    response = client.get(f"/admin/performance/by_user/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["user_id"] == test_user.id
    assert data["total_points"] == test_performance.points