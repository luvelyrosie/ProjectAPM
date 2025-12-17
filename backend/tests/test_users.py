from .utils import *
from fastapi import status
from app.main import app
from app.dependencies import get_db, get_current_user_from_cookie

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user_from_cookie] = override_get_current_user


def test_login_page():
    response = client.get("/users/login-page")
    assert response.status_code == status.HTTP_200_OK
    assert "login" in response.text.lower()


def test_register_page():
    response = client.get("/users/register-page")
    assert response.status_code == status.HTTP_200_OK
    assert "register" in response.text.lower()


def test_create_user_redirect():
    data = {
        "username": "newuser",
        "email": "newuser@test.com",
        "password": "password123",
        "role": "user"
    }
    response = client.post("/users/create-user", data=data, follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert "access_token" in response.headers.get("set-cookie", "")


def test_create_user_already_exists(test_user):
    data = {
        "username": test_user.username,
        "email": test_user.email,
        "password": "password123",
        "role": test_user.role
    }
    response = client.post("/users/create-user", data=data)
    
    assert response.status_code == 200
    assert "User already exists" in response.text


def test_login_html_success(test_user: User):
    data = {
        "username": test_user.username,
        "password": "test1234"
    }
    response = client.post("/users/login", data=data, follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert "access_token" in response.headers.get("set-cookie", "")


def test_login_html_invalid():
    data = {
        "username": "wronguser",
        "password": "wrongpass"
    }
    response = client.post("/users/login", data=data)
    assert response.status_code == status.HTTP_200_OK
    assert "Invalid credentials" in response.text


def test_login_api_success(test_user: User):
    data = {
        "username": test_user.username,
        "password": "test1234"
    }
    response = client.post(
        "/users/api/login",
        data=data,
        headers={"content-type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert "access_token" in json_data
    assert json_data["token_type"] == "bearer"


def test_login_html_invalid_credentials():
    data = {"username": "wronguser", "password": "wrongpass"}
    response = client.post("/users/login", data=data)
    assert response.status_code == 200
    assert "invalid credentials" in response.text.lower()


def test_logout_redirect():
    response = client.get("/users/logout", follow_redirects=False)
    assert response.status_code == 302
    assert 'access_token=""' in response.headers.get("set-cookie", "")