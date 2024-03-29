import sys
from logging import PercentStyle, StreamHandler
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from uvicorn.config import LOGGING_CONFIG
from uvicorn.logging import DefaultFormatter

from daemon import logger
from tests._utils import mock_list


class TestLogger(IsolatedAsyncioTestCase):
    @patch("daemon.logger.SentryAsgiMiddleware")
    @patch("daemon.logger.ignore_logger")
    @patch("daemon.logger.LoggingIntegration")
    @patch("daemon.logger.SqlalchemyIntegration")
    @patch("daemon.logger.AioHttpIntegration")
    @patch("daemon.logger.logging")
    @patch("daemon.logger.sentry_sdk.init")
    async def test__setup_sentry(
        self,
        sentry_sdk_init_patch: MagicMock,
        logging_patch: MagicMock,
        aiohttpintegration_patch: MagicMock,
        sqlalchemyintegration_patch: MagicMock,
        loggingintegration_patch: MagicMock,
        ignore_logger_patch: MagicMock,
        sentryasgimiddleware_patch: MagicMock,
    ):
        app, dsn, name, version = mock_list(4)

        logger.setup_sentry(app, dsn, name, version)

        aiohttpintegration_patch.assert_called_once_with()
        sqlalchemyintegration_patch.assert_called_once_with()
        loggingintegration_patch.assert_called_once_with(level=logging_patch.DEBUG, event_level=logging_patch.WARNING)
        sentry_sdk_init_patch.assert_called_once_with(
            dsn=dsn,
            attach_stacktrace=True,
            shutdown_timeout=5,
            integrations=[aiohttpintegration_patch(), sqlalchemyintegration_patch(), loggingintegration_patch()],
            release=f"{name}@{version}",
        )
        ignore_logger_patch.assert_called_once_with("uvicorn.error")
        app.add_middleware.assert_called_once_with(sentryasgimiddleware_patch)

    async def test__logging_formatter(self):
        self.assertIsInstance(logger.logging_formatter, DefaultFormatter)
        self.assertEqual("[%(asctime)s] %(levelprefix)s %(message)s", logger.logging_formatter._fmt)
        self.assertEqual("[%(asctime)s] %(levelprefix)s %(message)s", LOGGING_CONFIG["formatters"]["default"]["fmt"])
        self.assertEqual(
            '[%(asctime)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
            LOGGING_CONFIG["formatters"]["access"]["fmt"],
        )
        self.assertIsInstance(logger.logging_formatter._style, PercentStyle)

    async def test__logging_handler(self):
        self.assertIsInstance(logger.logging_handler, StreamHandler)
        self.assertIs(sys.__stdout__, logger.logging_handler.stream)
        self.assertIs(logger.logging_formatter, logger.logging_handler.formatter)

    @patch("daemon.logger.LOG_LEVEL")
    @patch("daemon.logger.logging_handler")
    @patch("daemon.logger.logging.getLogger")
    async def test__get_logger(
        self,
        getlogger_patch: MagicMock,
        logging_handler_patch: MagicMock,
        log_level_patch: MagicMock,
    ):
        name = MagicMock()

        result = logger.get_logger(name)

        getlogger_patch.assert_called_once_with(name)
        getlogger_patch().addHandler.assert_called_once_with(logging_handler_patch)
        log_level_patch.upper.assert_called_once_with()
        getlogger_patch().setLevel.assert_called_once_with(log_level_patch.upper())
        self.assertEqual(result, getlogger_patch())
