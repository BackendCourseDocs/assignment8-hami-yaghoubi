from tables import Author,Book
import database
from faker import Faker
import random

fake = Faker()

def create_authors(session, count=10):
    authors = []
    for _ in range(count):
        author = Author(
            name=fake.name()
        )
        authors.append(author)
    session.add_all(authors)
    session.commit()
    return authors

def create_books(session, authors, count=50):
    books = []
    for _ in range(count):
        book = Book(
            author_id=random.choice(authors).id,
            title=fake.unique.sentence(nb_words=3),
            publisher=fake.company(),
            cover_image=fake.binary(length=2048),
            published_date=fake.date_between("-2y", "today")
        )
        books.append(book)
    session.bulk_save_objects(books)
    session.commit()

def seed():
    database.init_db()
    session = database.sessionLocal()
    authors = create_authors(session, count=15)
    create_books(session, authors, count=120)
    session.close()


if __name__ == "__main__":
    seed()