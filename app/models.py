from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserDelete(BaseModel):
    email: EmailStr
    password: str


class Book(BaseModel):
    title: str
    author: str
    quantity: int


class BorrowedBookRequest(BaseModel):
    book_id: int
    reader_id: int


class ReturnBookRequest(BaseModel):
    book_id: int
    reader_id: int
