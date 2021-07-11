import sys

import uvicorn

from .daemon import app
from .environment import SENTRY_DSN, API_TOKEN, DEBUG, HOST, PORT, RELOAD
from .logger import get_logger, setup_sentry

logger = get_logger(__name__)


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

    uvicorn.run("daemon.daemon:app", host=HOST, port=PORT, reload=RELOAD)


def main():
    """Main function of the Python Daemon"""

    if SENTRY_DSN:
        setup_sentry(app, SENTRY_DSN, "python-daemon", "0.1.0")

    check_api_token()
    run_daemon()
