from fastapi import HTTPException

from app.data_base import get_db_connection


def get_readers():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email
        FROM readers
        """
    )

    reader_rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return [{
        "id": rr[0],
        "name": rr[1],
        "email": rr[2]}
        for rr in reader_rows
    ]


def get_reader(reader_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            name,
            email
        FROM readers
        WHERE id = %s
        """,
        (reader_id,)
    )

    reader_row = cursor.fetchone()
    cursor.close()
    connection.close()

    if reader_row is None:
        raise HTTPException(status_code=404, detail=f"Reader was not found with this id")

    return {
        "id": reader_row[0],
        "name": reader_row[1],
        "email": reader_row[2]
    }
