from passlib.context import CryptContext
from pydantic import  BaseModel, EmailStr

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


class UserCreate(BaseModel):
    email: EmailStr
    password: str