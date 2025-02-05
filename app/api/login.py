import jwt
from jwt.exceptions import PyJWTError
import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash

from .db import database
from .db_manager import get_user_by_name


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = os.environ.get('DATABASE_URL') or 'SECRET_KEY_LOCAL'
ALGORITHM = os.environ.get('ALGORITHM') or 'HS256'


async def create_jwt_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def authenticate_user(username: str, password: str):
    user = await get_user_by_name(username=username)

    if not user:
        return False
    if not check_password_hash(user.password_hash, password):
        return False
    return user


@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный логин или пароль",
        )
    access_token = await create_jwt_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        
    except PyJWTError:
        raise credentials_exception
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")

    if username:
        user = await get_user_by_name(username=username)
        return user

    return None