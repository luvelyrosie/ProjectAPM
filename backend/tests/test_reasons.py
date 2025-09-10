from .utils import *
from fastapi import status


def test_read_all_reject_reasons(test_user, test_reject_reason):
    response = client.get("/reject_reasons/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(reason["id"] == test_reject_reason.id for reason in data)


def test_get_reject_reason_by_id_success(test_user, test_reject_reason):
    response = client.get(f"/reject_reasons/{test_reject_reason.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_reject_reason.id
    assert data["description"] == test_reject_reason.description


def test_get_reject_reason_by_id_not_found(test_user):
    response = client.get("/reject_reasons/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    
def test_get_reject_reason_by_invalid_id(test_user):
    response = client.get("/reject_reasons/-1")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY