from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship

from app.database_by_alchemy import Base


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRemove(BaseModel):
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


class BookAlcCreate(BaseModel):
    title: str
    author: str
    quantity: int

    class Config:
        from_attributes = True


class BookAlcResponse(BaseModel):
    id: int
    title: str
    author: str
    quantity: int

    class Config:
        from_attributes = True


class ReaderAlcCreate(BaseModel):
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class ReaderAlcResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserAlc(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


class BookAlc(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String)
    quantity = Column(Integer)

    borrowed_books = relationship("BorrowedBookAlc", back_populates="book")

    def __repr__(self):
        return (f"<Book("
                f"id={self.id},"
                f"title={self.title},"
                f"author={self.author},"
                f"quantity={self.quantity}"
                f")>")


class ReaderAlc(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    borrowed_books = relationship("BorrowedBookAlc", back_populates="reader")

    def __repr__(self):
        return f"<Reader(id={self.id}, name={self.name}, email={self.email})>"


class BorrowedBookAlc(Base):
    __tablename__ = "borrowed_books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    reader_id = Column(Integer, ForeignKey('readers.id'))
    borrowed_date = Column(TIMESTAMP)
    returned_date = Column(TIMESTAMP)

    book = relationship('BookAlc', back_populates='borrowed_books')
    reader = relationship('ReaderAlc', back_populates="borrowed_books")

    def __repr__(self):
        return (f"<BorrowedBooks("
                f"id={self.id},"
                f"book_id={self.book_id},"
                f"reader_id={self.reader_id},"
                f"borrowed_date={self.borrowed_date},"
                f"returned_date={self.returned_date}"
                f")>")
