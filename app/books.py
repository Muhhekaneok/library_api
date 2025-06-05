from fastapi import HTTPException
from datetime import datetime

from app.data_base import get_db_connection
from app.database_by_alchemy import SessionLocal
from app.models import (BorrowedBookRequest, ReturnBookRequest, BookAlc,
                        BorrowedBookAlc, BookAlcCreate, Book)


def get_book():
    db = SessionLocal()
    db_books = db.query(BookAlc).all()
    db.close()
    return db_books


def add_book(book: BookAlcCreate):
    db = SessionLocal()
    db_book = BookAlc(title=book.title, author=book.author, quantity=book.quantity)

    existing_book = db.query(BookAlc).filter(BookAlc.title == book.title).first()
    if existing_book:
        db.close()
        raise HTTPException(status_code=400, detail="Book with this title already exist")

    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    db.close()
    return db_book


def update_book(book_id: int, book: Book):
    db = SessionLocal()
    db_book = db.query(BookAlc).filter(BookAlc.id == book_id).first()
    if not db_book:
        db.close()
        raise HTTPException(status_code=404, detail="Book not found")

    db_book.title = book.title
    db_book.author = book.author
    db_book.quantity = book.quantity

    db.commit()
    db.refresh(db_book)
    db.close()
    return db_book


def delete_book(book_id: int):
    db = SessionLocal()
    db_book = db.query(BookAlc).filter(BookAlc.id == book_id).first()
    if not db_book:
        db.close()
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(db_book)
    db.commit()
    db.close()
    # return BookAlcResponse(
    #     id=db_book.id,
    #     title=db_book.title,
    #     author=db_book.author,
    #     quantity=db_book.quantity
    # )
    return {"message": "Book successfully deleted"}


def borrow_book(request: BorrowedBookRequest):
    db = SessionLocal()
    db_book = db.query(BookAlc).filter(BookAlc.id == request.book_id).first()
    if not db_book:
        db.close()
        raise HTTPException(status_code=404, detail="No available copies of this book")

    db_borrowed_book = db.query(BorrowedBookAlc).filter(BorrowedBookAlc.reader_id == request.reader_id,
                                                        BorrowedBookAlc.returned_date == None).all()

    if len(db_borrowed_book > 3):
        db.close()
        raise HTTPException(status_code=400, detail="Reader has already borrowed 3 books")

    new_borrow = BorrowedBookAlc(book_id=request.book_id,
                                 reader_id=request.reader_id,
                                 borrowed_date=datetime.now())

    db.add(new_borrow)
    db.commit()
    db.refresh(new_borrow)
    db.close()

    db_book.quantity -= 1
    db.commit()
    return {"message": "Book successfully borrowed"}


def return_book(request: ReturnBookRequest):
    db = SessionLocal()
    db_borrow = db.query(BorrowedBookAlc).filter(BorrowedBookAlc.book_id == request.book_id,
                                                 BorrowedBookAlc.reader_id == request.reader_id,
                                                 BorrowedBookAlc.returned_date == None).first()

    if not db_borrow:
        db.close()
        raise HTTPException(status_code=400, detail="This book wasn't borrow by this reader")

    db_borrow.returned_date = datetime.now()
    db.commit()

    db_book = db.query(BookAlc).filter(BookAlc.id == request.book_id).first()
    db_book.quantity += 1
    db.commit()
    db.close()
    return {"message": "Book successfully returned"}


def get_all_borrowed_and_returned_books():
    db = SessionLocal()
    db_borrowed_books = db.query(BorrowedBookAlc).all()
    db.close()
    return db_borrowed_books


def get_borrowed_book_by_reader(reader_id: int):
    db = SessionLocal()
    db_borrowed_books_by_reader = (db.query(BorrowedBookAlc)
                                   .filter(BorrowedBookAlc.reader_id == reader_id).all())
    if not db_borrowed_books_by_reader:
        db.close()
        raise HTTPException(status_code=404, detail="No borrowed books found for this reader")
    return db_borrowed_books_by_reader


def get_only_borrowed_books():
    db = SessionLocal()
    db_only_borrowed = db.query(BorrowedBookAlc).filter(BorrowedBookAlc.returned_date == None).all()

    if not db_only_borrowed:
        db.close()
        raise HTTPException(status_code=404, detail="No borrowed books found")

    db.close()
    return db_only_borrowed