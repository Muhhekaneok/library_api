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
        f"INSERT INTO books (title, author) VALUES"
        f"{book.title, book.author} RETURNING id"
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
