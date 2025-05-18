from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from app.db_config import db_config

app = FastAPI()


class Book(BaseModel):
    title: str
    author: str


@app.get("/")
def read_root():
    return {"message": "Library API is running"}


@app.get("/books")
def get_books():
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT id, title, author FROM books")
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [{
        "id": r[0],
        "title": r[1],
        "author": r[2]}
        for r in rows
    ]


@app.post("/books")
def add_book(book: Book):
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(
        "INSERT INTO books (title, author) VALUES (%s, %s) RETURNING id",
        (book.title, book.author)
    )
    new_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return [{
        "id": new_id,
        "title": book.title,
        "author": book.author
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