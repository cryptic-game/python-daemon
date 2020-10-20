import os


def get_bool(key: str, default: bool) -> bool:
    return os.getenv(key, str(default)).lower() in ("true", "t", "yes", "y", "1")


API_TOKEN = os.getenv("API_TOKEN")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = get_bool("DEBUG", False)
SQL_SERVER_LOCATION = os.getenv("SQL_SERVER_LOCATION", "postgresql://localhost:5432")
SQL_SERVER_DATABASE = os.getenv("SQL_SERVER_DATABASE", "cryptic")
SQL_SERVER_USERNAME = os.getenv("SQL_SERVER_USERNAME", "cryptic")
SQL_SERVER_PASSWORD = os.getenv("SQL_SERVER_PASSWORD", "cryptic")
SQL_SHOW_STATEMENTS = get_bool("SQL_SHOW_STATEMENTS", False)
