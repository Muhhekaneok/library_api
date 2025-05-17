from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Library API is running"}


@app.get("/books")
def get_books():
    return [
        {"id": 1, "title": "Three men in a boat", "author": "Gerome K. Jerome"},
        {"id": 2, "title": "Spin Dictators", "author": "Sergey Guriev"},
        {"id": 3, "title": "Изучаем Python", "author": "Eric Matthes"},
        {"id": 4, "title": "Статистика и котики", "author": "Владимир Савельев"}
    ]