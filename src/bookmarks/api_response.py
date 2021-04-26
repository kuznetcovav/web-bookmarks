from __future__ import annotations

import dataclasses
import functools
from http import HTTPStatus
import json
from typing import Any, Callable, Dict, List, Optional

import flask


@dataclasses.dataclass
class ApiResponse:
    data: dict
    status: str
    error_message: Optional[str]
    http_status: HTTPStatus
    
    @staticmethod
    def error(error_message: str, http_status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> ApiResponse:
        return ApiResponse(data={}, status='error', error_message=error_message, http_status=http_status)

    @staticmethod
    def success(data: Any, http_status: HTTPStatus = HTTPStatus.OK) -> ApiResponse:
        return ApiResponse(data=data, status='success', error_message=None, http_status=http_status)

    def _make_api_response(self, app: flask.Flask, is_public_api: bool) -> flask.Response:
        resp = app.make_response(json.dumps({
                'data': self.data,
                'status': self.status,
                'error_message': self.error_message or '',
            }, ensure_ascii=False))
        
        resp.status_code = self.http_status.value
        
        resp.mimetype = 'application/json; charset=utf-8'
        if is_public_api:
            resp.headers['Access-Control-Allow-Origin'] = '*'
            
        return resp

    def make_public_response(self, app: flask.Flask) -> flask.Response:
        return self._make_api_response(app, is_public_api=True)

    def make_private_response(self, app: flask.Flask) -> flask.Response:
        return self._make_api_response(app, is_public_api=False)


def public_api(app: flask.Flask):
    def wrapped_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ret: ApiResponse = func(*args, **kwargs)
            except:
                ret = ApiResponse.error('Internal server error', HTTPStatus.INTERNAL_SERVER_ERROR)
            return ret.make_public_response(app)
        return wrapper
    return wrapped_decorator


def private_api(app: flask.Flask):
    def wrapped_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ret: ApiResponse = func(*args, **kwargs)
            except:
                ret = ApiResponse.error('Internal server error', HTTPStatus.INTERNAL_SERVER_ERROR)
            return ret.make_private_response(app)
        return wrapper
    return wrapped_decorator
