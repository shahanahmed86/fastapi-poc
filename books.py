from fastapi import FastAPI, Body

app = FastAPI()

BOOKS = [
    {"title": "Title One", "author": "Author One", "category": "Science"},
    {"title": "Title Two", "author": "Author Two", "category": "Science"},
    {"title": "Title Three", "author": "Author Three", "category": "History"},
    {"title": "Title Four", "author": "Author Four", "category": "Math"},
    {"title": "Title Five", "author": "Author Five", "category": "Math"},
    {"title": "Title Six", "author": "Author Two", "category": "Math"},
]


@app.get("/books")
async def read_all_books():
    return BOOKS


@app.get("/books/{title}")
async def read_book(title: str):
    for book in BOOKS:
        if book.get("title").casefold() == title.casefold():
            return book


@app.get("/books/")
async def read_books_by_category(category: str):
    filtered_books = []

    for book in BOOKS:
        if book.get("category").casefold() == category.casefold():
            filtered_books.append(book)

    return filtered_books


@app.get("/books/{author}/")
async def read_books_by_author_then_category(author: str, category: str):
    filtered_books = []

    for book in BOOKS:
        is_author_found = book.get("author").casefold() == author.casefold()
        is_category_found = book.get("category").casefold() == category.casefold()

        if is_author_found and is_category_found:
            filtered_books.append(book)

    return filtered_books


@app.post("/books")
async def create_book(book=Body()):
    BOOKS.append(book)
    return book


@app.put("/books")
async def update_book(update_book=Body()):
    for i in range(len(BOOKS)):
        book = BOOKS[i]
        if book.get("title").casefold() == update_book.get("title").casefold():
            BOOKS[i] = update_book

    return update_book


@app.delete("/books/{title}")
async def delete_book(title: str):
    for i in range(len(BOOKS)):
        if BOOKS[i].get("title").casefold() == title.casefold():
            return BOOKS.pop(i)
