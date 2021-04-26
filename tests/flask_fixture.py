import dataclasses
import os
import pathlib
import tempfile

import pytest

import bookmarks.config as config


@pytest.fixture(name='db_path', autouse=True, scope='session')
def _db_path():
    """
    Create exactly one temporary DB file per session.
    The api fixture would then create & delete it for every
    API test case.
    """
    
    db_path = tempfile.mktemp()
    config.DB_CONNECT_STRING = f'sqlite:///{db_path}'
    
    yield pathlib.Path(db_path)


@pytest.fixture(name='api')
def _api(db_path):
    from bookmarks._db_init import create_database
    from bookmarks.api import app
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            create_database()
        yield client

    db_path.unlink()


@pytest.fixture(name='api_route')
def _api_route():
    return config.api_route


@pytest.fixture(name='db_session')
def _db_session():
    from bookmarks.schema import ScopedSession
    with ScopedSession() as session:
        yield session

@pytest.fixture(name='add_bookmark')
def _add_bookmark(db_session):
    from bookmarks.schema import ScopedSession
    
    def _add_bookmark_impl(bookmark):
        db_session.add(bookmark)
        db_session.commit()

    yield _add_bookmark_impl


@pytest.fixture(name='get_all_bookmarks')
def _get_bookmarks(db_session):
    from bookmarks.schema import ScopedSession
    from bookmarks.bookmark import Bookmark
    
    def _get_bookmarks_impl():
        return db_session.query(Bookmark).all()

    yield _get_bookmarks_impl