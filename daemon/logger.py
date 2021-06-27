import logging
import sys

import sentry_sdk
from fastapi import FastAPI
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration, ignore_logger
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from environment import LOG_LEVEL


def setup_sentry(app: FastAPI, dsn: str, name: str, version: str):
    """Initialize sentry connection."""

    sentry_sdk.init(
        dsn=dsn,
        attach_stacktrace=True,
        shutdown_timeout=5,
        integrations=[
            AioHttpIntegration(),
            SqlalchemyIntegration(),
            LoggingIntegration(
                level=logging.DEBUG,
                event_level=logging.WARNING,
            ),
        ],
        release=f"{name}@{version}",
    )
    ignore_logger("uvicorn.error")
    app.add_middleware(SentryAsgiMiddleware)


logging_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")

logging_handler = logging.StreamHandler(sys.stdout)
logging_handler.setFormatter(logging_formatter)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with a given name."""

    logger: logging.Logger = logging.getLogger(name)
    logger.addHandler(logging_handler)
    logger.setLevel(LOG_LEVEL.upper())

    return logger
