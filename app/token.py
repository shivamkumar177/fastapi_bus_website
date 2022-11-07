from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

SECRET_KEY = '824822203904f0788e1728a49574f297d8dd5f68b5d3bd5a4d348fb0a8877070'
ALGORITHM = 'HS256'

def create_access_token(data: dict):
    to_encode = data.copy()
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm= ALGORITHM)
    return encoded

def verify_password(user_password: str, hashed_password: str):
    return pwd_context.verify(user_password, hashed_password)

def decode_jwt(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        print(e)

def get_password_hash(password: str):
    return pwd_context.hash(password)