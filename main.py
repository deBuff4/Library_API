import sqlite3
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def init():
    return "Hello message"

# 1. CRUD для книг
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

# Работа с рецензиями

@app.get("/books/{id}/reviews")
def get_review(id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'SELECT title, comment FROM books '
              f' JOIN reviews ON books.id = reviews.book_id'
              f'WHERE books.id = {id}')

    out = c.fetchall()
    db.commit()
    db.close()
    return out

# Специальные эндпоинты
@app.get("/books/list/recomendations")
def book_recs():
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute("""SELECT title, AVG(rating) AS average_rating FROM books 
              JOIN reviews ON books.id = reviews.book_id
              GROUP BY title 
              ORDER BY average_rating DESC 
              LIMIT 5""")
    rating = c.fetchall()

    db.commit()
    db.close()

    return rating




