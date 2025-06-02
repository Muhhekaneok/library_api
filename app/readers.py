from fastapi import HTTPException

from app.data_base import get_db_connection
from app.database_by_alchemy import SessionLocal
from app.models import ReaderAlc


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
