import sqlite3
from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class NewBook(BaseModel):
    title: str
    author: str
    year: int
    genre: str
    is_read: bool

class UpdateBook(BaseModel):
    title: str | None = 'None'
    author: str | None = 'None'
    year: int | None = 0
    genre: str | None = 'None'
    is_read: bool | None = 0

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

@app.post("/books")
def add_book(new_book: NewBook):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'INSERT INTO books (title, author, year, genre, is_read) '
              f'VALUES (?, ?, ?, ?, ?)',                        # Плейсхолдеры для безопасной передачи данных  в SQLite
              (new_book.title, new_book.author, new_book.year, new_book.genre, new_book.is_read))

    db.commit()
    db.close()
    return {"status": "Created"}

@app.put("/books/{id}")                     # Обновление информации о книге
def update_book_info(update_info: UpdateBook, id: str):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'UPDATE books '
              f'SET title = ?, '
              f'author = ?, '
              f'year = ?, '
              f'genre = ?, '
              f'is_read = ? '
              f'WHERE books.id = {id}', (update_info.title, update_info.author, update_info.year, update_info.genre, update_info.is_read))

    db.commit()
    db.close()

@app.delete("/books/{id}")
def delete_book(id: int):               # Удаление книги вместе с рецензиями к ней

    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'DELETE FROM books WHERE books.id = {id} ')
    c.execute(f'DELETE FROM reviews WHERE reviews.book_id = {id} ')

    db.commit()
    db.close()

    return {"status": "Deleted"}

# 2. Работа с рецензиями

@app.get("/books/{id}/reviews")         # Вывод рецензий по определенной книге
def get_review(id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'SELECT title, comment FROM books '
              f'JOIN reviews ON books.id = reviews.book_id '
              f'WHERE books.id = {id}')

    out = c.fetchall()
    db.commit()
    db.close()
    return out

# 3. Специальные эндпоинты
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


@app.patch("/books/{id}/toggle-read")
def switch_is_read_status(id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'UPDATE books '
              f'SET is_read = NOT is_read '
              f'WHERE books.id = {id};')

    db.commit()
    db.close()
