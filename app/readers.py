from fastapi import HTTPException

from app.data_base import get_db_connection
from app.database_by_alchemy import SessionLocal
from app.models import ReaderAlc, ReaderAlcCreate


def get_readers():
    db = SessionLocal()
    db_readers = db.query(ReaderAlc).all()
    db.close()

    return db_readers


def get_reader(reader_id: int):
    db = SessionLocal()
    db_reader = db.query(ReaderAlc).filter(ReaderAlc.id == reader_id).first()
    if not db_reader:
        db.close()
        raise HTTPException(status_code=404, detail="Reader not found")

    return db_reader


def add_reader(reader: ReaderAlcCreate):
    db = SessionLocal()
    db_reader = ReaderAlc(name=reader.name, email=reader.email)

    existing_reader = db.query(ReaderAlc).filter(ReaderAlc.email == reader.email).first()
    if existing_reader:
        db.close()
        raise HTTPException(status_code=400, detail="Reader with this email already exist")

    db.add(db_reader)
    db.commit()
    db.refresh(db_reader)
    db.close()

    return db_reader


def delete_reader(reader_id: int):
    db = SessionLocal()
    db_reader = db.query(ReaderAlc).filter(ReaderAlc.id == reader_id).first()
    if not db_reader:
        db.close()
        raise HTTPException(status_code=404, detail="Reader not found")

    db.delete(db_reader)
    db.commit()
    db.close()

    return {"message": "Reader successfully deleted"}