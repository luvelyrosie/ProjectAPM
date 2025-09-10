from .utils import *
from fastapi import status


def test_read_all_tasks(test_user, test_task):
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(t["id"] == test_task.id for t in data)


def test_get_task_by_id(test_user, test_task):
    response = client.get(f"/tasks/{test_task.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_task.id
    assert data["name"] == test_task.name


def test_update_task(test_user, test_task):
    payload = {"name": "Updated Task Name", "status": "В работе"}
    response = client.put(f"/tasks/update-taks/{test_task.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    updated = response.json()
    assert updated["name"] == payload["name"]
    assert updated["status"] == payload["status"]


def test_get_tasks_by_operator(test_user, test_task):
    response = client.get(f"/tasks/by_operator/{test_user.id}")
    assert response.status_code == status.HTTP_200_OK
    tasks = response.json()
    assert any(t["id"] == test_task.id for t in tasks)


def test_start_task_success(test_user, test_task):
    response = client.post(f"/tasks/{test_task.id}/start")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "В работе"


def test_start_task_invalid_status(test_user, test_task, db):
    test_task.status = "Готово"
    db.commit()
    db.refresh(test_task)

    response = client.post(f"/tasks/{test_task.id}/start")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_complete_task_success(test_user, test_task, db):
    test_task.status = "В работе"
    db.commit()
    db.refresh(test_task)

    response = client.post(f"/tasks/{test_task.id}/complete")
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == "Готово"
    assert "end_time" in body


def test_complete_task_invalid_status(test_user, test_task):
    response = client.post(f"/tasks/{test_task.id}/complete")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_reject_task_success(test_user, test_task):
    data = {"description": "Incorrect assembly"}
    response = client.post(f"/tasks/{test_task.id}/reject", json=data)
    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["status"] == "Брак"
    assert body["reject_reason"] == data["description"]


def test_reject_task_missing_reason(test_user, test_task):
    response = client.post(f"/tasks/{test_task.id}/reject", json={})
    assert response.status_code == status.HTTP_400_BAD_REQUEST