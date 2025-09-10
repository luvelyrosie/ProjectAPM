from .utils import *
from fastapi import status


def test_read_all_workstations(test_workstation):
    response = client.get("/workstations/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(ws["id"] == test_workstation.id for ws in data)


def test_get_workstation_by_id(test_workstation):
    response = client.get(f"/workstations/{test_workstation.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_workstation.id
    assert data["name"] == test_workstation.name


def test_get_workstation_by_id_not_found():
    response = client.get("/workstations/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "not found" in data["detail"].lower()