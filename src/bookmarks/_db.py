from contextlib import contextmanager
from typing import Iterator

import sqlalchemy.orm
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from bookmarks import config


engine = create_engine(config.DB_CONNECT_STRING)
Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)


@contextmanager
def ScopedSession() -> Iterator[sqlalchemy.orm.Session]:
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
