from typing import List

from fastapi import FastAPI, Depends, HTTPException

from app.auth import create_access_token, get_current_user
from app.books import (get_book, add_book, update_book, delete_book, borrow_book,
                       return_book, get_borrowed_book_by_reader, get_all_borrowed_books)
from app.models import (UserCreate, UserLogin, UserRemove, Book, BorrowedBookRequest, ReturnBookRequest,
                        UserAlc, BookAlc, ReaderAlc, BorrowedBookAlc, BookAlcCreate, BookAlcResponse)
from app.readers import get_readers, get_reader
from app.users import register, login, remove, get_all_users
from app.database_by_alchemy import SessionLocal

app = FastAPI()


@app.post("/register_user")
def register_user(user: UserCreate):
    return register(user)


@app.post("/login_user")
def login_user(user: UserLogin):
    return login(user)


@app.get("/users")
def get_users_sqlalchemy():
    return get_all_users()


@app.delete("/delete_user")
def delete_user(user: UserRemove):
    return remove(user)


@app.get("/books", response_model=List[BookAlcResponse])
def get_book_sqlalchemy():
    return get_book()


@app.post("/books", response_model=BookAlcResponse)
def add_book_sqlalchemy(book: BookAlcCreate, current_user: str = Depends(get_current_user)):
    return add_book(book)


@app.put("/book/{book_id}", response_model=BookAlcResponse)
def update_book_sqlalchemy(book_id: int, book: BookAlcCreate, current_user: str = Depends(get_current_user)):
    return update_book(book_id, book)


# @app.delete("/book/{book_id}", response_model=BookAlcResponse)
@app.delete("/book/{book_id}", response_model=None)
def delete_book_sqlalchemy(book_id: int, current_user: str = Depends(get_current_user)):
    return delete_book(book_id)


@app.get("/readers")
def get_readers_sqlalchemy():
    return get_readers()


@app.get("/readers/{reader_id}")
def get_reader_sqlalchemy(reader_id: int):
    return get_reader(reader_id)


@app.post("/borrow")
def borrow_book_sqlalchemy(borrow_req: BorrowedBookRequest):
    return borrow_book(borrow_req)


@app.get("/borrowed_books")
def get_all_borrowed_books_sqlalchemy():
    return get_all_borrowed_books()


@app.get("/borrowed_books/{reader_id}")
def get_borrowed_books_by_reader_sqlalchemy(reader_id: int):
    return get_borrowed_book_by_reader(reader_id)
