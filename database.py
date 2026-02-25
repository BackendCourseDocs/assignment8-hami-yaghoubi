from sqlalchemy import URL,create_engine
from sqlalchemy.orm import sessionmaker
from tables import Base
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = URL.create(
    drivername=os.getenv("DRIVER_NAME"),
    username=os.getenv("USER_NAME"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT")
)

engine = create_engine(DB_URL)


sessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)