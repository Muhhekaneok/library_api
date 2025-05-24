from fastapi import HTTPException
from datetime import datetime

from app.data_base import get_db_connection
from app.models import Book, BorrowedBookRequest, ReturnBookRequest


def get_book():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            id,
            title,
            author,
            quantity
        FROM books
        """
    )

    books_rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return [{
        "id": br[0],
        "title": br[1],
        "author": br[2],
        "quantity": br[3]}
        for br in books_rows
    ]


def add_book(book: Book):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO books (title, author, quantity)
        VALUES (%s, %s, %s) RETURNING id
        """,
        (book.title, book.author, book.quantity)
    )

    new_id = cursor.fetchone()[0]
    connection.commit()
    cursor.close()
    connection.close()

    return {
        "id": new_id,
        "title": book.title,
        "author": book.author,
        "quantity": book.quantity
    }


def update_book(book_id: int, book: Book):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE books
        SET title = %s, author = %s, quantity = %s
        WHERE id = %s  
        """,
        (book.title, book.author, book.quantity, book_id)
    )

    connection.commit()
    updated_rows = cursor.rowcount
    cursor.close()
    connection.close()

    if updated_rows == 0:
        raise HTTPException(status_code=404,
                            detail=f"Error: book with id = {book_id} not found")

    return {
        "message": "Book successfully updated"
    }


def delete_book(book_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM borrowed_books
        WHERE book_id = %s
        """,
        (book_id,)
    )

    cursor.execute(
        """
        DELETE FROM books WHERE id = %s
        """,
        (book_id,)
    )

    connection.commit()
    deleted_rows = cursor.rowcount
    cursor.close()
    connection.close()

    if deleted_rows == 0:
        raise HTTPException(status_code=404,
                            detail=f"Error: book with id = {book_id} not found")

    return {
        "message": "Book successfully deleted"
    }


def borrow_book(request: BorrowedBookRequest):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT quantity FROM books
        WHERE id = %s
        """,
        (request.book_id,)
    )
    result = cursor.fetchone()
    if not result:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="Book not found")

    quantity = result[0]
    if quantity <= 0:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="No available copies of this book")

    cursor.execute(
        """
        SELECT count(*) FROM borrowed_books
        WHERE reader_id = %s AND returned_date IS NULL
        """,
        (request.reader_id,)
    )
    books_borrow = cursor.fetchone()[0]
    if books_borrow > 3:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="Three books has already borrowed")

    cursor.execute(
        """
        INSERT INTO borrowed_books (book_id, reader_id, borrowed_date)
        VALUES (%s, %s, %s)
        """,
        (request.book_id, request.reader_id, datetime.now())
    )

    cursor.execute(
        """
        UPDATE books SET quantity = quantity - 1
        WHERE id = %s 
        """,
        (request.book_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "message": "Book successfully borrowed"
    }


def return_book(request: ReturnBookRequest):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            book_id,
            reader_id,
            borrowed_books,
            returned_date
        FROM borrowed_books
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
        "message": "Book successfully returned"
    }


def get_borrowed_book_by_reader(reader_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.id,
            b.title,
            b.author,
            bb.reader_id,
            bb.borrowed_date
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
        "author": br[2],
        "reader_id": br[3],
        "borrowed_date": br[4]}
        for br in book_rows
    ]


def get_all_borrowed_books():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            b.id,
            b.title,
            b.author,
            bb.id,
            r.name
        FROM books AS b
        JOIN borrowed_books AS bb
        ON b.id = bb.book_id
        JOIN readers as r
        ON r.id = bb.reader_id
        WHERE bb.returned_date IS NULL
        """
    )

    borrowed_books = cursor.fetchall()
    cursor.close()
    connection.close()

    return [{
        "id": bb[0],
        "title": bb[1],
        "author": bb[2],
        "borrowed_id": bb[3],
        "reader": bb[4]}
        for bb in borrowed_books
    ]
