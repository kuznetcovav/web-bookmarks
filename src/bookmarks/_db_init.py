from bookmarks._db_base import Base
from bookmarks._db import engine


def create_database() -> None:
    Base.metadata.create_all(engine)
