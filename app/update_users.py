from app.auth import hash_password
from app.database_by_alchemy import SessionLocal
from app.models import UserAlc

def update_users():
    db = SessionLocal()
    db_users = db.query(UserAlc).filter(UserAlc.hashed_password == None).all()

    for db_user in db_users:
        db_user.hashed_password = hash_password("super-mega_password")
        db.commit()

    db.close()

if __name__ == "__main__":
    update_users()
    print("Users updated successfully")