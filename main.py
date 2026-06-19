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

class UpdateReview(BaseModel):
    rating: int
    comment: str
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

@app.post("/books/{id}/reviews")
def add_review(new_review: UpdateReview, id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'SELECT EXISTS (SELECT 1 FROM reviews WHERE book_id = {id})')
    existing = bool(c.fetchone()[0])

    if existing:
        c.execute(f'UPDATE reviews r '
                  f'SET r.rating = ?, '
                  f'r.comment = ? '
                  f'WHERE r.book_id == {id}', (new_review.rating, new_review.comment))

    elif not existing:
        c.execute(f'INSERT INTO reviews (book_id,rating, comment) '
              f'VALUES ({id}, ?, ?) '
              f';', (new_review.rating, new_review.comment))

    else: return "Error"

    db.commit()
    db.close()

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

@app.delete("/reviews/{id}")
def delete_review(id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'DELETE FROM reviews WHERE id = {id};')

    db.commit()
    db.close()

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

@app.get("/stats")
def statistics():
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'SELECT COUNT(id) AS count_books, '
        f'COUNT(is_read) FILTER (WHERE is_read = 1) AS count_is_read, '
        f'ROUND(AVG(year)) AS round_avg_year, '
        f'(SELECT genre FROM books GROUP BY genre ORDER BY COUNT(genre) DESC LIMIT 1) FROM books '
        f'LIMIT 3')
    stats = c.fetchall()[0]
    dict_stats = [("count books", stats[0]), ("count is read", stats[1]), ("round avg year", stats[2]), ("best genre", stats[3])]       # Потом надо перевести в норм JSON
    db.commit()
    db.close()
    return dict_stats

@app.patch("/books/{id}/toggle-read")
def switch_is_read_status(id: int):
    db = sqlite3.connect("books_database.db")
    c = db.cursor()

    c.execute(f'UPDATE books '
              f'SET is_read = NOT is_read '
              f'WHERE books.id = {id};')

    db.commit()
    db.close()

