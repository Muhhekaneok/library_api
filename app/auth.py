from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

get_token = OAuth2PasswordBearer(tokenUrl="/login")

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


SECRET_KEY = "abcdefgABCDEFG"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 45


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(token: str = Depends(get_token)) -> str:
    try:
        decoded_data = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        email = decoded_data.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
