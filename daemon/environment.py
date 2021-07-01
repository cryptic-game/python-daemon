from os import getenv


def get_bool(key: str, default: bool) -> bool:
    """
    Get a boolean value from the environment variables

    :param key: key of the env var
    :param default: default value
    :return: the boolean value
    """

    return getenv(key, str(default)).lower() in ("true", "t", "yes", "y", "1")


LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO")

HOST = getenv("HOST", "0.0.0.0")  # noqa: S104
PORT = int(getenv("PORT", "8000"))
RELOAD = get_bool("RELOAD", False)
DEBUG = get_bool("DEBUG", False)

API_TOKEN = getenv("API_TOKEN")

# database configuration
DB_DRIVER: str = getenv("SQL_DRIVER", "postgresql+asyncpg")
DB_HOST: str = getenv("SQL_HOST", "localhost")
DB_PORT: int = int(getenv("SQL_PORT", "5432"))
DB_DATABASE: str = getenv("SQL_DATABASE", "cryptic")
DB_USERNAME: str = getenv("SQL_USERNAME", "cryptic")
DB_PASSWORD: str = getenv("SQL_PASSWORD", "cryptic")
POOL_RECYCLE: int = int(getenv("POOL_RECYCLE", "300"))
POOL_SIZE: int = int(getenv("POOL_SIZE", "20"))
MAX_OVERFLOW: int = int(getenv("MAX_OVERFLOW", "20"))
SQL_SHOW_STATEMENTS: bool = get_bool("SQL_SHOW_STATEMENTS", False)
SQL_CREATE_TABLES: bool = get_bool("SQL_CREATE_TABLES", False)

# redis configuration
REDIS_HOST = getenv("REDIS_HOST", "redis")
REDIS_PORT = int(getenv("REDIS_PORT", "6379"))
REDIS_DB = int(getenv("REDIS_DB", "0"))

SENTRY_DSN: str = getenv("SENTRY_DSN")  # sentry data source name
