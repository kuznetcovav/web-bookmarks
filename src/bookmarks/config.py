import pathlib

from decouple import config

API_PREFIX: str = config('API_PREFIX', default='/api/v1')

DB_CONNECT_STRING: str = config('DB_CONNECT_STRING')

WORKING_DIR: pathlib.Path = pathlib.Path(config('WORKING_DIR'))
LOGS_DIR: pathlib.Path = WORKING_DIR.joinpath(pathlib.Path(config('LOGS_DIR')))

SECRET_KEY: str = config('SECRET_KEY')

TIMEZONE: str = config('TIMEZONE')


def get_log_path(filename: str) -> pathlib.Path:
    return LOGS_DIR.joinpath(filename)


# relative_route must start with a /.
def api_route(relative_route: str) -> str:
    return API_PREFIX + relative_route