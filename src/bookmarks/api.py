import json
import logging
from typing import Dict, List, Union

import flask

import bookmarks.config as config
from bookmarks.log import get_logger, redirect_basic_logging


L = get_logger('api', logging.DEBUG)
redirect_basic_logging(L, logging.INFO)

app = flask.Flask(__name__)
app.secret_key = config.SECRET_KEY


def _make_api_response(obj: dict) -> flask.Response:
    resp = app.make_response(json.dumps(obj, ensure_ascii=False))
    resp.mimetype = 'application/json; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


@app.route('/api/hello')
def index_json() -> flask.Response:
    return _make_api_response({'Hello': 'World'})
