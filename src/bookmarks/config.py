import pathlib

from decouple import config


DB_CONNECT_STRING: str = config('DB_CONNECT_STRING')

WORKING_DIR: pathlib.Path = pathlib.Path(config('WORKING_DIR'))
LOGS_DIR: pathlib.Path = WORKING_DIR.joinpath(pathlib.Path(config('LOGS_DIR')))

SECRET_KEY: str = config('SECRET_KEY')

TIMEZONE: str = config('TIMEZONE')

DEFAULT_LIST_LIMIT: int = config('DEFAULT_LIST_LIMIT', cast=int)
MAX_LIST_LIMIT: int = config('MAX_LIST_LIMIT', cast=int)


def get_log_path(filename: str) -> pathlib.Path:
    return LOGS_DIR.joinpath(filename)
