from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from .database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Request
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from .models import User
from datetime import timedelta, datetime, timezone
from jose import jwt, JWTError
from fastapi import status


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
   
        
db_dependency=Annotated[Session, Depends(get_db)]
bcrypt_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/users/api/login")
SECRET_KEY='f0d6e9c1a5b8f72c3d4e5a96708b1c4a5f6e7d8c9a0b1c2d3e4f5a6b7c8d9e0f'
ALGORITHM='HS256'


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
        
        
async def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            return None  # ⬅️ instead of raising
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        return None
        
    
user_dependency=Annotated[dict, Depends(get_current_user)]
user_dependency_cookie=Annotated[dict, Depends(get_current_user_from_cookie)]

templates = Jinja2Templates(directory="frontend/templates")

def redirect_to_login():
    redirect_response = RedirectResponse(url="/users/login-page", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie(key="access_token")
    return redirect_response