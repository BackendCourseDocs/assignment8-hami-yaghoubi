from sqlalchemy import Integer,String,LargeBinary,Date,ForeignKey
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,relationship
from datetime import date


class Base(DeclarativeBase):
    pass

class Author(Base):
    __tablename__ = "authors"
    id : Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    name : Mapped[str] = mapped_column(String)
    books : Mapped[list["Book"]] = relationship("Book",back_populates="author")


class Book(Base):
    __tablename__ = "books"
    id : Mapped[int] = mapped_column(Integer,primary_key=True,autoincrement=True)
    author_id : Mapped[int] = mapped_column(Integer,ForeignKey("authors.id"))
    title : Mapped[str] = mapped_column(String(100))
    publisher : Mapped[str] = mapped_column(String(100),nullable=True)
    cover_image : Mapped[bytes] = mapped_column(LargeBinary,nullable=True)
    published_date : Mapped[date] = mapped_column(Date)
    author: Mapped["Author"] = relationship("Author", back_populates="books")
