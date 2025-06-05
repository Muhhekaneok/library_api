from typing import List

from fastapi import FastAPI, Depends

from app.auth import get_current_user
from app.models import (UserCreate, UserLogin, UserRemove, Book, BorrowedBookRequest,
                        BookAlcCreate, BookAlcResponse, ReaderAlcCreate, ReaderAlcResponse, ReturnBookRequest)
from app.users import register, login, remove, get_all_users
from app.books import (get_book, add_book, update_book, delete_book, borrow_book, return_book,
                       get_borrowed_book_by_reader, get_all_borrowed_and_returned_books, get_only_borrowed_books)
from app.readers import get_readers, get_reader, add_reader, delete_reader

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
def delete_user(user: UserRemove, current_user: str = Depends(get_current_user)):
    return remove(user)


@app.get("/books", response_model=List[BookAlcResponse])
def get_book_sqlalchemy():
    return get_book()


@app.post("/books", response_model=BookAlcResponse)
def add_book_sqlalchemy(book: BookAlcCreate, current_user: str = Depends(get_current_user)):
    return add_book(book)


@app.put("/book/{book_id}", response_model=BookAlcResponse)
def update_book_sqlalchemy(book_id: int, book: Book, current_user: str = Depends(get_current_user)):
    return update_book(book_id, book)


# @app.delete("/book/{book_id}", response_model=BookAlcResponse)
@app.delete("/book/{book_id}", response_model=None)
def delete_book_sqlalchemy(book_id: int, current_user: str = Depends(get_current_user)):
    return delete_book(book_id)


@app.get("/readers", response_model=List[ReaderAlcResponse])
def get_readers_sqlalchemy():
    return get_readers()


@app.get("/readers/{reader_id}", response_model=ReaderAlcResponse)
def get_reader_sqlalchemy(reader_id: int):
    return get_reader(reader_id)


@app.post("/readers", response_model=ReaderAlcResponse)
def add_reader_sqlalchemy(reader: ReaderAlcCreate):
    return add_reader(reader)


@app.delete("/reader/{reader_id}", response_model=None)
def delete_reader_sqlalchemy(reader_id: int):
    return delete_reader(reader_id)


@app.post("/borrow")
def borrow_book_sqlalchemy(borrow_req: BorrowedBookRequest):
    return borrow_book(borrow_req)


@app.post("/return")
def return_book_sqlalchemy(return_req: ReturnBookRequest):
    return return_book(return_req)


@app.get("/borrowed_and_returned_books")
def get_all_borrowed_and_returned_books_sqlalchemy():
    return get_all_borrowed_and_returned_books()


@app.get("/borrowed_books/{reader_id}")
def get_borrowed_books_by_reader_sqlalchemy(reader_id: int):
    return get_borrowed_book_by_reader(reader_id)


@app.get("/borrowed_books_only")
def get_only_borrowed_books_sqlalchemy():
    return get_only_borrowed_books()