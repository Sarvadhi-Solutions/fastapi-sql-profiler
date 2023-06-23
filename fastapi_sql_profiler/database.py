import os

from dotenv import load_dotenv

# from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()


Base = declarative_base()


def get_db():
    """Coroutine generator function for getting a database session.

    This function returns a generator that yields a database session object.
    The session is retrieved from the `SessionLocal` object, which represents
    a thread-local session.

    Usage:
    ```
    with get_db() as db:
        # Use the database session `db` here
    # The session is automatically closed and returned to the connection pool
    ```
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
