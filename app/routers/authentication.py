from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app import database, models, token
from datetime import datetime

router = APIRouter(tags=['Auth'])

@router.post('/login')
def login(request: OAuth2PasswordRequestForm = Depends()):
    fetch_user = database.get_user(request.username)
    if not fetch_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found!")
    fetch_user['_id'] = str(fetch_user['_id'])
    user = models.User(**fetch_user)
    if not token.verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Wrong Password")
    data = {"sub": user.email}
    access_token = token.create_access_token(data)
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/sign-up')
def create_user(request: models.createUser):
    user_email = request.email
    user_name = request.full_name
    user_password = request.password
    if not (user_email and user_name and user_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Please Provide all the details!")
    # check for existing user
    fetch_user = database.get_user(user_email)
    if fetch_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User already exists!")
    user_role = "user"
    # handle for admin (domain_check, etc)
    new_user = {
        "email": user_email,
        "full_name": user_name,
        "hashed_password": token.get_password_hash(user_password),
        "role": user_role,
        "created_at": datetime.utcnow()
    }
    created_user_id = database.add_data("users", new_user)
    return {"message": "User Created Successfully", "user_id": str(created_user_id)}