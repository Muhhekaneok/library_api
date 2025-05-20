from fastapi import FastAPI, HTTPException, Depends, Security
from pydantic import BaseModel
import psycopg2
from app.db_config import db_config
from app.auth import hash_password, verify_password, UserCreate, create_access_token, UserLogin, get_current_user
from datetime import datetime

app = FastAPI(
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": False
    }
)


class Book(BaseModel):
    title: str
    author: str
    quantity: int


class ReturnRequest(BaseModel):
    book_id: str
    reader_id: str


@app.get("/")
def read_root():
    return {"message": "Library API is running"}


@app.get("/books")
def get_books():
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, author, quantity FROM books")
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{
        "id": r[0],
        "title": r[1],
        "author": r[2],
        "quantity": r[3]}
        for r in rows
    ]


@app.post("/books")
def add_book(book: Book, current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO books (title, author, quantity) VALUES (%s, %s, %s) RETURNING id",
        (book.title, book.author, book.quantity)
    )
    new_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return [{
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "quantity": book.quantity
    }]


@app.put("/books/{book_id}")
def update_book(book_id: int, book: Book):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE books SET title = %s, author = %s WHERE id = %s",
        (book.title, book.author, book_id)
    )

    connection.commit()
    updated_rows = cursor.rowcount
    cursor.close()
    connection.close()

    if updated_rows == 0:
        return {"Error": f"Book with id = {book_id} not found"}

    return {
        "id": book_id,
        "title": book.title,
        "author": book.author
    }


@app.delete("/books/{book_id")
def delete_book(book_id: int):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(
        "DELETE FROM books WHERE id = %s",
        (book_id,)
    )

    connection.commit()
    deleted_rows = cursor.rowcount
    cursor.close()
    connection.close()

    if deleted_rows == 0:
        return {"Error": f"Book with id = {book_id} not found"}

    return {
        "message": f"Book with id = {book_id} was deleted"
    }


@app.post("/register")
def register(user: UserCreate):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (user.email,)
    )
    if cursor.fetchone():
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (email, hashed_password) VALUES (%s, %s)",
        (user.email, hashed_password)
    )
    connection.commit()
    cursor.close()
    connection.close()

    return {
        "message": "User registered"
    }


@app.post("/login")
def login(user: UserLogin):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (user.email,)
    )
    db_user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, email, hashed_password = db_user

    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": email})

    return {
        "access_token": access_token, "token_type": "bearer"
    }


class BorrowedRequest(BaseModel):
    book_id: int
    reader_id: int


@app.post("/borrow")
def borrow_book(request: BorrowedRequest, current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT quantity FROM books WHERE id = %s",
        (request.book_id,)
    )
    result = cursor.fetchone()

    if not result:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=401, detail="Book not found")

    quantity = result[0]
    if quantity <= 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No available copies of this book")

    cursor.execute(
        """
        SELECT COUNT(*) FROM borrowed_books
        WHERE reader_id = %s AND returned_date IS NULL
        """,
        (request.reader_id,)
    )

    books_borrowed = cursor.fetchone()[0]
    if books_borrowed >= 3:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="3 books has already borrowed")

    cursor.execute(
        """
        INSERT INTO borrowed_books (book_id, reader_id, borrowed_date)
        VALUES (%s, %s, %s)
        """,
        (request.book_id, request.reader_id, datetime.now())
    )

    cursor.execute(
        "UPDATE books SET quantity = quantity - 1 WHERE id = %s",
        (request.book_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "message": "Book borrowed"
    }


@app.post("/return")
def return_book(request: ReturnRequest,
                current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT * FROM borrowed_books
        WHERE book_id = %s AND reader_id = %s AND returned_date IS NULL
        """,
        (request.book_id, request.reader_id)
    )

    borrow = cursor.fetchone()
    if not borrow:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400,
                            detail="Book isn't borrowed by this reader")

    borrow_id = borrow[0]
    cursor.execute(
        """
        UPDATE borrowed_books
        SET returned_date = %s
        WHERE id = %s
        """,
        (datetime.now(), borrow_id)
    )

    cursor.execute(
        """
        UPDATE books
        SET quantity = quantity + 1
        WHERE id = %s
        """,
        (request.book_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "message": "Book returned"
    }


@app.get("/borrowed/{reader_id}")
def get_borrowed_books(reader_id: int, current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.id,
            b.title,
            b.author
        FROM books AS b
        JOIN borrowed_books AS bb
        ON b.id = bb.book_id
        WHERE bb.reader_id = %s AND bb.returned_date IS NULL
        """,
        (reader_id,)
    )

    book_rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return [{
        "id": br[0],
        "title": br[1],
        "author": br[2]}
        for br in book_rows
    ]


@app.get("/users")
def get_users(current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")
    user_rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{
        "id": ur[0],
        "email": ur[1]}
        for ur in user_rows
    ]


@app.get("/readers")
def get_readers(current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute("SELECT id, name, email FROM readers")
    readers_rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{
        "id": rr[0],
        "name": rr[1],
        "email": rr[2]}
        for rr in readers_rows
    ]


@app.get("/readers/{reader_id}")
def get_reader(reader_id: int, current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email
        FROM readers
        WHERE id = %s
        """,
        (reader_id,)
    )

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if row is None:
        raise HTTPException(status_code=404,
                            detail="Reader with such id was not found")

    return {
        "id": row[0],
        "name": row[1],
        "email": row[2]
    }


@app.get("/borrowed")
def get_all_borrowed_books(current_user: str = Depends(get_current_user)):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.id,
            b.title,
            r.name,
            bb.borrowed_date
        FROM books AS b
        JOIN borrowed_books AS bb ON b.id = bb.book_id
        JOIN readers AS r ON r.id = bb.reader_id
        WHERE bb.returned_date IS NULL
        """
    )

    borrowed_rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return [{
        "book_id": br[0],
        "title": br[1],
        "reader_name": br[2],
        "borrowed_date": br[3]}
        for br in borrowed_rows
    ]
