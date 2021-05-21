import os


def get_bool(key: str, default: bool) -> bool:
    """
    Get a boolean value from the environment variables

    :param key: key of the env var
    :param default: default value
    :return: the boolean value
    """

    return os.getenv(key, str(default)).lower() in ("true", "t", "yes", "y", "1")


API_TOKEN = os.getenv("API_TOKEN")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = get_bool("DEBUG", False)
SQL_SERVER_LOCATION = "postgresql://" + os.getenv("SQL_HOST", "localhost") + ":" + os.getenv("SQL_PORT", "5432")
SQL_SERVER_DATABASE = os.getenv("SQL_DB", "cryptic")
SQL_SERVER_USERNAME = os.getenv("SQL_USER", "cryptic")
SQL_SERVER_PASSWORD = os.getenv("SQL_PASS", "cryptic")
SQL_SHOW_STATEMENTS = get_bool("SQL_SHOW_STATEMENTS", False)
SQL_CREATE_TABLES = get_bool("SQL_CREATE_TABLES", False)
SENTRY_DSN = os.getenv("SENTRY_DSN", None)
