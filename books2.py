from typing import Optional
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()


class Book:
    id: int
    title: str
    description: str
    author: str
    rating: int
    published_year: int

    def __init__(
        self,
        id: int,
        title: str,
        author: str,
        description: str,
        rating: int,
        published_year: int,
    ):
        self.id = id
        self.title = title
        self.author = author
        self.description = description
        self.rating = rating
        self.published_year = published_year


class BookRequest(BaseModel):
    title: str = Field(min_length=3, max_length=50)
    description: str = Field(min_length=3, max_length=100)
    author: str = Field(min_length=3, max_length=50)
    rating: int = Field(gt=0, lt=6)
    published_year: int = Field(gt=1999, lt=2024)

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "A new book",
                "author": "codingwithroby",
                "description": "A new description",
                "rating": 5,
                "published_year": 2024,
            }
        }
    }


BOOKS = [
    Book(1, "Computer Science Pro", "codingwithroby", "A very nice book", 5, 2021),
    Book(2, "Be Fast with FastAPI", "codingwithroby", "A great book", 5, 2022),
    Book(3, "Master Endpoints", "codingwithroby", "A Awesome book", 5, 2022),
    Book(4, "HP1", "Author 1", "Book Description", 2, 2023),
    Book(5, "HP2", "Author 2", "Book Description", 3, 2023),
    Book(6, "HP3", "Author 3", "Book Description", 1, 2021),
]


@app.get("/books", status_code=status.HTTP_200_OK)
async def get_all_books(
    rating: Optional[int] = Query(None, gt=0, lt=6),
    published_year: Optional[int] = Query(None, gt=1999, lt=2024),
):
    if rating is None and published_year is None:
        return BOOKS

    filtered_books = []

    for book in BOOKS:
        has_rating = rating is not None and book.rating == rating
        has_published_year = (
            published_year is not None and book.published_year >= published_year
        )

        if has_rating and has_published_year:
            filtered_books.append(book)
        elif has_rating:
            filtered_books.append(book)
        elif has_published_year:
            filtered_books.append(book)

    return filtered_books


@app.get("/books/{book_id}", status_code=status.HTTP_200_OK)
async def read_book_by_id(book_id: int = Path(gt=0)):
    for book in BOOKS:
        if book.id == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(data: BookRequest):
    id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
    new_book = Book(id=id, **data.model_dump())
    BOOKS.append(new_book)

    return new_book


@app.put("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_book(data: BookRequest, book_id: int = Path(gt=0)):
    book_changed = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS[i] = Book(id=book_id, **data.model_dump())
            book_changed = True
            break

    if not book_changed:
        raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int = Path(gt=0)):
    book_deleted = False

    for i in range(len(BOOKS)):
        if BOOKS[i].id == book_id:
            BOOKS.pop(i)
            book_deleted = True
            break

    if not book_deleted:
        raise HTTPException(status_code=404, detail="Book not found")
