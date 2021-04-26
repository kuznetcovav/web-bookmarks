import dataclasses
from http import HTTPStatus
import json
import logging
from typing import Dict, List, Optional

import flask

from bookmarks._db_init import create_database
from bookmarks.api_response import ApiResponse, public_api, private_api
import bookmarks.config as config
from bookmarks.log import get_logger, redirect_basic_logging
from bookmarks.schema import Bookmark, ScopedSession


api_route = config.api_route

L = get_logger('api', logging.DEBUG)
redirect_basic_logging(L, logging.INFO)

app = flask.Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.before_first_request
def init_app():
    create_database()


# GET bookmark
@app.route(api_route('/bookmarks/<string:bookmark_id_str>'), methods=['GET'])
@public_api(app)
def bookmarks_get(bookmark_id_str: str) -> ApiResponse:
    try:
        bookmark_id = int(bookmark_id_str)
    except ValueError:
        return ApiResponse.error('Invalid bookmark id (should be integer)')
    
    with ScopedSession() as session:
        bookmark: Optional[Bookmark] = session.query(Bookmark).get(bookmark_id)
        if bookmark is None:
            return ApiResponse.error('Bookmark not found', HTTPStatus.NOT_FOUND)
        else:
            return ApiResponse.success(bookmark.serialize())


# GET bookmarks list
@app.route(api_route('/bookmarks'), methods=['GET'])
@public_api(app)
def bookmarks_list() -> ApiResponse:
    with ScopedSession() as session:
        total_count = session.query(Bookmark).count()
        
        bookmarks = session.query(Bookmark).all()
        bookmarks_serialized = [bookmark.serialize() for bookmark in sorted(bookmarks, key=lambda b: b.id)]
        return ApiResponse.success(bookmarks_serialized)


@dataclasses.dataclass
class _BookmarkParseResult:
    bookmark: Optional[Bookmark]
    error_response: Optional[ApiResponse]


def _parse_bookmark(data: bytes) -> _BookmarkParseResult:
    try:
        bookmark_dict = json.loads(data)
    except json.JSONDecodeError as e:
        return _BookmarkParseResult(None, ApiResponse.error(f'JSON decoding error: {"".join(e.args)}'))
    
    try:
        bookmark = Bookmark.deserialize_ignore_id(bookmark_dict)
    except ValueError as e:
        return _BookmarkParseResult(None, ApiResponse.error(f'Invalid bookmark data: {"".join(e.args)}'))

    return _BookmarkParseResult(bookmark, None)


# Create new bookmark
@app.route(api_route('/bookmarks'), methods=['POST'])
@public_api(app)
def bookmarks_post() -> ApiResponse:
    res = _parse_bookmark(flask.request.data)
    if res.error_response is not None:
        return res.error_response
    
    new_bookmark: Bookmark = res.bookmark
    
    with ScopedSession() as session:
        session.add(new_bookmark)
        session.flush()
        return ApiResponse.success(new_bookmark.serialize(), HTTPStatus.CREATED)


# Update an existing bookmark
@app.route(api_route('/bookmarks/<string:bookmark_id_str>'), methods=['PUT'])
@public_api(app)
def bookmarks_put(bookmark_id_str: str) -> ApiResponse:
    try:
        bookmark_id = int(bookmark_id_str)
    except ValueError:
        return ApiResponse.error('Invalid bookmark id (should be integer)')

    res = _parse_bookmark(flask.request.data)
    if res.error_response is not None:
        return res.error_response
    
    new_bookmark: Bookmark = res.bookmark
    new_bookmark.id = bookmark_id
    
    with ScopedSession() as session:
        old_bookmark = session.query(Bookmark).get(bookmark_id)
        if old_bookmark is None:
            return ApiResponse.error(f'Adding new bookmarks with an arbitrary IDs is not allowed', HTTPStatus.FORBIDDEN)
        
        new_bookmark = session.merge(new_bookmark)
        session.flush()
        
        return ApiResponse.success(new_bookmark.serialize())


# Delete an existing bookmark
@app.route(api_route('/bookmarks/<string:bookmark_id_str>'), methods=['DELETE'])
@public_api(app)
def bookmarks_delete(bookmark_id_str: str) -> ApiResponse:
    try:
        bookmark_id = int(bookmark_id_str)
    except ValueError:
        return ApiResponse.error('Invalid bookmark id (should be integer)')
    
    with ScopedSession() as session:
        session.query(Bookmark).filter(Bookmark.id == bookmark_id).delete()
        return ApiResponse.success({})
