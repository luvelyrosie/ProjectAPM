from .utils import *
from fastapi import status


def test_read_all_logs(test_user, test_maintenance_log):
    response = client.get("/maintenance_logs/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(log["id"] == test_maintenance_log.id for log in data)


def test_create_log_success(test_user, test_workstation):
    payload = {
        "workstation_id": test_workstation.id,
        "type": "Inspection",
        "description": "Routine check"
    }
    response = client.post("/maintenance_logs/create-logs", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["type"] == payload["type"]
    assert data["description"] == payload["description"]


def test_read_log_by_id_success(test_user, test_maintenance_log):
    response = client.get(f"/maintenance_logs/{test_maintenance_log.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_maintenance_log.id
    assert data["description"] == test_maintenance_log.description


def test_read_log_by_id_not_found(test_user):
    response = client.get("/maintenance_logs/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_log_success(test_user, test_maintenance_log):
    payload = {
        "type": "Repair",
        "description": "Updated description"
    }
    response = client.put(f"/maintenance_logs/update-logs/{test_maintenance_log.id}", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == payload["description"]


def test_update_log_not_found(test_user):
    payload = {"type": "Repair", "description": "Does not exist"}
    response = client.put("/maintenance_logs/update-logs/99999", json=payload)
    assert response.status_code == status.HTTP_404_NOT_FOUND