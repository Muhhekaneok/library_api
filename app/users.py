from fastapi import HTTPException

from app.auth import hash_password, verify_password, create_access_token
from app.data_base import get_db_connection
from app.database_by_alchemy import SessionLocal
from app.models import UserCreate, UserLogin, UserRemove, UserAlc


def register(user: UserCreate):
    db = SessionLocal()
    db_user = db.query(UserAlc).filter(UserAlc.email == user.email).first()
    if db_user:
        db.close()
        raise HTTPException(status_code=400, detail="User already registered")

    hashed_password = hash_password(user.password)
    db_user = UserAlc(email=user.email, hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return {"message": "User successfully registered"}


def get_user_by_email(email: str):
    db = SessionLocal()
    db_user = db.query(UserAlc).filter(UserAlc.email == email).first()
    db.close()
    return db_user


def get_all_users():
    db = SessionLocal()
    db_users = db.query(UserAlc).all()
    db.close()
    return db_users


def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def remove(user: UserRemove):
    db = SessionLocal()
    db_user = db.query(UserAlc).filter(UserAlc.email == user.email).first()

    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        db.close()
        raise HTTPException(status_code=403, detail="Invalid password")

    total_users = db.query(UserAlc).count()
    if total_users <= 1:
        db.close()
        raise HTTPException(status_code=400, detail="At least one user must exist")

    db.delete(db_user)
    db.commit()
    db.close()
    return {"message": "User successfully deleted"}
