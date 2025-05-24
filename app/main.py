from fastapi import FastAPI, Depends

from app.auth import create_access_token, get_current_user
from app.books import (get_book, add_book, update_book, delete_book, borrow_book, return_book,
                       get_borrowed_book_by_reader, get_all_borrowed_books)
from app.models import UserCreate, UserLogin, UserDelete, Book, BorrowedBookRequest, ReturnBookRequest
from app.readers import get_readers, get_reader
from app.users import register, login, delete, get

app = FastAPI()


@app.post("/register_user")
def register_user(user: UserCreate):
    return register(user)


@app.post("/login_user")
def login_user(user: UserLogin):
    user_id, user_email = login(user)
    assess_token = create_access_token(data={"sub": user_email})
    return {
        "access_token": assess_token, "token_type": "bearer"
    }


@app.get("/")
def read_root():
    return {"message": "Library API is running"}


@app.get("/books")
def get_books_view():
    return get_book()


@app.post("/books")
def add_book_view(book: Book, current_user: str = Depends(get_current_user)):
    return add_book(book)


@app.put("/books/{book_id}")
def update_book_view(book_id: int, book: Book):
    return update_book(book_id, book)


@app.delete("/books/{book_id}")
def delete_book_view(book_id: int):
    return delete_book(book_id)


@app.get("/users")
def get_users(current_user: str = Depends(get_current_user)):
    return get()


@app.delete("/delete_user")
def delete_user(user: UserDelete):
    return delete(user)


@app.get("/readers")
def get_readers_view(current_user: str = Depends(get_current_user)):
    return get_readers()


@app.get("/readers/{reader_id}")
def get_reader_view(reader_id: int, current_user: str = Depends(get_current_user)):
    return get_reader(reader_id)


@app.post("/borrow")
def borrow_book_view(request: BorrowedBookRequest,
                     current_user: str = Depends(get_current_user)):
    return borrow_book(request)


@app.post("/return")
def return_book_view(request: ReturnBookRequest,
                     current_user: str = Depends(get_current_user)):
    return return_book(request)


@app.get("/borrowed")
def get_all_borrowed(current_user: str = Depends(get_current_user)):
    return get_all_borrowed_books()


@app.get("/borrowed/{reader_id}")
def get_borrowed_books_by_reader_id(reader_id: int,
                                    current_user: str = Depends(get_current_user)):
    return get_borrowed_book_by_reader(reader_id)
