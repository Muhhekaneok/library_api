import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

LOGIN_URL = "/login"
BORROW_URL = "/borrow"
BOOKS_URL = "/books"

TEST_EMAIL = "joebiden@biden.com"
TEST_PASSWORD = "oldjoe"


def get_token():
    login_response = client.post(
        LOGIN_URL,
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
    )
    assert login_response.status_code == 200
    return login_response.json()["access_token"]


def test_protected_post_books_no_token():
    response = client.post(
        BOOKS_URL,
        json={
            "title": "Test Book",
            "author": "Test Author"
        }
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_borrow_unavailable_book():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        BORROW_URL,
        headers=headers,
        json={"book_id": 10, "reader_id": 1}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No available copies of this book"


def test_protected_endpoint_wo_token():
    response = client.post(
        BORROW_URL,
        json={"book_id": 1, "reader_id": 1}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"