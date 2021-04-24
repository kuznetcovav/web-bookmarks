from bookmarks._db import Base, engine


def create_database() -> None:
    Base.metadata.create_all(engine)
