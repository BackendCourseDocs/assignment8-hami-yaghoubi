from fastapi import FastAPI, Query, UploadFile, File, Form, Depends, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from typing import List
import database
from tables import Author,Book
from sqlalchemy.orm import Session,selectinload
from sqlalchemy import or_,select,func
from datetime import date

books_cache = {}
authors_cache = {}


database.init_db()

app = FastAPI()


def get_db():
    db = database.sessionLocal()
    try:
        yield db
    finally:
        db.close()

class BookModel(BaseModel):
    id: int
    title: str = Field(..., min_length=3, max_length=100)
    author: str = Field(..., min_length=3, max_length=100)
    publisher: str | None = Field(None, min_length=3, max_length=100)
    published_date : date = Field(...)
    cover_url: str | None = None

class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[BookModel]


class AuthorWithBookCount(BaseModel):
    id: int
    name: str
    book_count: int

class AuthorSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[AuthorWithBookCount]



@app.post("/books", response_model=BookModel, status_code=201)
def add_book(
    title: str = Form(...),
    author: str = Form(...),
    publisher: str | None = Form(None, min_length=3, max_length=100),
    published_date: date = Form(...),
    cover_image: UploadFile = File(None),
    db : Session = Depends(get_db)
    ):

    content = None
    if cover_image and cover_image.filename:
        content = cover_image.file.read()

    publisher_value = publisher.strip() if publisher else None

    query = select(Author).where(Author.name == author.strip())
    author_obj = db.execute(query).scalar_one_or_none()

    if not author_obj:
        author_obj = Author(name=author.strip())
        db.add(author_obj)
        db.commit()

    new_book = Book(title=title.strip(),author_id=author_obj.id,publisher=publisher_value,published_date=published_date,cover_image=content)
    db.add(new_book)
    db.commit()

    books_cache.clear()
    authors_cache.clear()

    return BookModel(
        id=new_book.id,
        title=title.strip(),
        author=author.strip(),
        publisher=publisher_value,
        published_date = published_date
    )


@app.get("/books", response_model=SearchResponse)
def get_books(
    request : Request,
    q: str | None = Query(None, min_length=3, max_length=100,alias="search-optional"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    

    cache_key = (q, page, page_size)

    if cache_key in books_cache:
        print("BOOKS CACHE HIT")
        return books_cache[cache_key]
    
    print("BOOKS DB QUERY")
    
    offset = (page - 1) * page_size

    query = select(Book).join(Book.author).options(selectinload(Book.author))

    if q:
        search = f"%{q.strip()}%"
        query = query.where(or_(Book.title.ilike(search),Author.name.ilike(search)))
    
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    result = db.execute(query.offset(offset).limit(page_size))
    books_orm = result.scalars().all()


    books = []
    for book in books_orm:
        cover_url = None
        if book.cover_image:
            cover_url = request.url_for("get_book_cover", book_id=book.id)
        books.append(BookModel(
            id=book.id,
            title=book.title,
            author=book.author.name,
            publisher=book.publisher,
            published_date=book.published_date,
            cover_url=str(cover_url) if cover_url else None
        ))

    total_pages = (total + page_size - 1) // page_size


    response = SearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=books
    )

    books_cache[cache_key] = response

    return response


@app.get("/books/{book_id}/cover")
def get_book_cover(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book or not book.cover_image:
        return JSONResponse(status_code=404, content={"detail": "Cover image not found"})
    return Response(content=book.cover_image, media_type="image/jpeg")

@app.get("/authors/search", response_model=AuthorSearchResponse)
def search_authors(
    q: str = Query(..., min_length=2, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    
    cache_key = (q, page, page_size)

    if cache_key in authors_cache:
        print("AUTHORS CACHE HIT")
        return authors_cache[cache_key]

    print("AUTHORS DB QUERY")


    offset = (page - 1) * page_size

    search = f"%{q.strip()}%"
    

    query = (
        select(Author, func.count(Book.id).label("book_count"))
        .outerjoin(Book, Author.id == Book.author_id)
        .where(Author.name.ilike(search))
        .group_by(Author.id)
    )
    

    total_query = select(func.count()).select_from(Author).where(Author.name.ilike(search))
    total = db.scalar(total_query)
    

    result = db.execute(query.offset(offset).limit(page_size))
    authors_with_counts = result.all()
    
    results = [
        AuthorWithBookCount(
            id=author.id,
            name=author.name,
            book_count=count
        )
        for author, count in authors_with_counts
    ]
    
    total_pages = (total + page_size - 1) // page_size
    
    response = AuthorSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=results
    )

    authors_cache[cache_key] = response

    return response