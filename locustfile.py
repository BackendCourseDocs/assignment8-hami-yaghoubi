from locust import HttpUser, task, between
import random


class LibraryUser(HttpUser):

    wait_time = between(1, 3)

    def on_start(self):
        self.book_ids = list(range(1, 50))

    @task(5)
    def get_books(self):
        page = random.randint(1, 5)
        self.client.get(
            f"/books?page={page}&page_size=10"
        )

    @task(3)
    def search_books(self):
        queries = ["python", "data", "code", "book"]
        q = random.choice(queries)

        self.client.get(
            f"/books?search-optional={q}&page=1&page_size=10"
        )

    @task(2)
    def search_authors(self):
        queries = [ "john", "ali", "mickel"]
        q = random.choice(queries)

        self.client.get(
            f"/authors/search?q={q}&page=1&page_size=10"
        )

    @task(1)
    def get_cover(self):
        book_id = random.choice(self.book_ids)
        self.client.get(f"/books/{book_id}/cover")