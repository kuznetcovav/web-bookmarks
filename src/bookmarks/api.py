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


L = get_logger('api', logging.DEBUG)
redirect_basic_logging(L, logging.INFO)

app = flask.Flask(__name__)
app.secret_key = config.SECRET_KEY


@app.before_first_request
def init_app():
    create_database()


# GET bookmark
@app.route('/api/bookmarks/<string:bookmark_id_str>', methods=['GET'])
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
# Params:
# - after_id (int, optional): the last bookmark on the previous page
# - limit (int, optional, less than DEFAULT_LIST_LIMIT): the maximum amount of entries in the list
@app.route('/api/bookmarks', methods=['GET'])
@public_api(app)
def bookmarks_list() -> ApiResponse:
    try:
        after_id = int(flask.request.args.get('after_id') or 0)
    except ValueError:
        return ApiResponse.error('Invalid after_id (should be integer)')
    
    try:
        limit = int(flask.request.args.get('limit') or config.DEFAULT_LIST_LIMIT)
    except ValueError:
        return ApiResponse.error('Invalid limit (should be integer)')
    
    if limit > config.MAX_LIST_LIMIT or limit <= 0:
        return ApiResponse.error(f'Invalid limit, should be positive and less than {config.MAX_LIST_LIMIT + 1}')
    
    with ScopedSession() as session:
        total_count = session.query(Bookmark).count()
        
        query = session.query(Bookmark).filter(Bookmark.id > after_id).limit(limit)
        bookmarks = query.all()
        bookmarks_serialized = [bookmark.serialize() for bookmark in sorted(bookmarks, key=lambda b: b.id)]
        return ApiResponse.success({'total_count': total_count, 'bookmarks': bookmarks_serialized})


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
        bookmark = Bookmark.deserialize_without_id(bookmark_dict)
    except ValueError as e:
        return _BookmarkParseResult(None, ApiResponse.error(f'Invalid bookmark data: {"".join(e.args)}'))

    return _BookmarkParseResult(bookmark, None)


# Create new bookmark
@app.route('/api/bookmarks', methods=['POST'])
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
@app.route('/api/bookmarks/<string:bookmark_id_str>', methods=['PUT'])
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
@app.route('/api/bookmarks/<string:bookmark_id_str>', methods=['DELETE'])
@public_api(app)
def bookmarks_delete(bookmark_id_str: str) -> ApiResponse:
    try:
        bookmark_id = int(bookmark_id_str)
    except ValueError:
        return ApiResponse.error('Invalid bookmark id (should be integer)')
    
    with ScopedSession() as session:
        session.query(Bookmark).filter(Bookmark.id == bookmark_id).delete()
        return ApiResponse.success({})
