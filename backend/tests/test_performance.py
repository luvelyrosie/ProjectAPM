from .utils import *
from fastapi import status


def test_create_performance(test_user, test_task):
    payload = {
        "user_id": test_user.id,
        "task_id": test_task.id,
        "points": 10
    }
    response = client.post("/performance/create-performance/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["user_id"] == payload["user_id"]
    assert data["task_id"] == payload["task_id"]
    assert data["points"] == payload["points"]


def test_get_performance_success(test_user, test_performance):
    response = client.get(f"/performance/performance/{test_performance.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_performance.id
    assert data["points"] == test_performance.points


def test_get_performance_not_found(test_user):
    response = client.get("/performance/performance/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_performance_success(test_user, test_performance):
    payload = {"points": test_performance.points + 5}
    response = client.put(f"/performance/performance/{test_performance.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["points"] == payload["points"]


def test_update_performance_not_found(test_user):
    payload = {"points": 100}
    response = client.put("/performance/performance/99999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND
