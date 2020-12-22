import sys

import sentry_sdk

from config import SENTRY_DSN, API_TOKEN, DEBUG, SQL_CREATE_TABLES
from daemon import run_daemon
from database import db


def setup_sentry():
    """Initialize sentry connection if environment variable is set"""

    if not SENTRY_DSN:
        return

    sentry_sdk.init(dsn=SENTRY_DSN, attach_stacktrace=True, shutdown_timeout=5)


def check_api_token():
    """Ensure that the api token environment variable is set"""

    if API_TOKEN:
        return

    if DEBUG:
        print("\033[33mWARNING: No API token specified, endpoints can be accessed without authentication!\033[0m")
    else:
        print("\033[31m\033[1mERROR: No API token specified!\033[0m")
        sys.exit(1)


def create_tables():
    """Create database tables if environment variable is set"""

    if not SQL_CREATE_TABLES:
        return

    db.Base.metadata.create_all(db.engine)


def main():
    """Main function of the Python Daemon"""

    setup_sentry()
    check_api_token()
    create_tables()
    run_daemon()


if __name__ == "__main__":
    main()
