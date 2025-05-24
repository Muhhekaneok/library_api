from fastapi import HTTPException

from app.auth import hash_password, verify_password
from app.data_base import get_db_connection
from app.models import UserCreate, UserLogin, UserDelete


def register(user: UserCreate):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            email,
            hashed_password
        FROM users
        WHERE email = %s
        """,
        (user.email,)
    )

    if cursor.fetchone():
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="User already registered")

    hashed_password = hash_password(user.password)
    cursor.execute(
        """
        INSERT INTO users (email, hashed_password) VALUES (%s, %s)
        """,
        (user.email, hashed_password)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "message": "User successfully registered"
    }


def get_user_by_email(email: UserLogin):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            email,
            hashed_password
        FROM users WHERE email = %s
        """,
        (email,)
    )
    db_user = cursor.fetchone()
    cursor.close()
    connection.close()

    return db_user


def login(user: UserLogin):
    db_user = get_user_by_email(user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, user_email, hashed_password = db_user
    if not verify_password(user.password, hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    return user_id, user_email


def get():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            email
        FROM users
        """
    )

    user_rows = cursor.fetchall()

    return [{
        "id": ur[0],
        "email": ur[1]}
        for ur in user_rows
    ]


def delete(user: UserDelete):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            hashed_password
        FROM users
        WHERE email = %s""",
        (user.email,)
    )
    result = cursor.fetchone()
    if not result:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")

    user_id, hashed_password = result
    if not verify_password(user.password, hashed_password):
        cursor.close()
        connection.close()
        raise HTTPException(status_code=403, detail="Invalid password")

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    if total_users <= 1:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=400, detail="At least one user must exist")

    cursor.execute(
        "DELETE FROM users WHERE id = %s",
        (user_id,)
    )

    connection.commit()
    cursor.close()
    connection.close()

    return {
        "message": "User successfully deleted"
    }
