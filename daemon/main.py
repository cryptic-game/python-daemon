import sys

import uvicorn

from daemon import app
from environment import SENTRY_DSN, API_TOKEN, DEBUG, HOST, PORT, RELOAD
from logger import get_logger, setup_sentry

logger = get_logger(__name__)
get_logger("uvicorn")


def check_api_token():
    """Ensure that the api token environment variable is set"""

    if API_TOKEN:
        return

    if DEBUG:
        logger.warning("No API token specified, endpoints can be accessed without authentication!")
    else:
        logger.error("No API token specified!")
        sys.exit(1)


def run_daemon():
    """Run the uvicorn http server"""

    uvicorn.run("daemon:app", host=HOST, port=PORT, reload=RELOAD, log_config=None)


def main():
    """Main function of the Python Daemon"""

    if SENTRY_DSN:
        setup_sentry(app, SENTRY_DSN, "python-daemon", "0.0.1")

    check_api_token()
    run_daemon()


if __name__ == "__main__":
    main()
