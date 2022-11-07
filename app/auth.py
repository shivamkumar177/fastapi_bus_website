from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app import database
from app.models import User
from app.token import decode_jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user_role_and_id(access_token = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_jwt(access_token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except Exception as e:
        print(e)
        raise credentials_exception
    fetch_user = database.get_user(username)
    if not fetch_user:
        raise credentials_exception
    fetch_user['_id'] = str(fetch_user['_id'])
    user = User(**fetch_user)
    if not user:
        raise credentials_exception
    return user
