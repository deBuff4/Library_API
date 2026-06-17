import sqlite3
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def init():
    return "Hello message"

@app.get("/books")          # Вывод всех книг
def get_books():
    db = sqlite3.connect("books_database.db")

    c = db.cursor()
    c.execute("""SELECT * FROM books""")
    out = c.fetchall()
    db.commit()
    db.close()

    return out

@app.get("/books/{id}")         # Поиск книги по ID
def get_book(id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()
    c.execute(f'SELECT  *, reviews.rating, reviews.comment FROM books, reviews '
              f'WHERE books.id = {id}')
    out = c.fetchall()
    c.execute(f'SELECT  AVG(rating) FROM reviews WHERE book_id = {id}')
    avg_rating = c.fetchone()
    db.commit()
    db.close()

    return out, f"AVERAGE RATING - {avg_rating}"




