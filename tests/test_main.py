from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, call

from daemon import main
from tests._utils import import_module, run_module


class TestMain(IsolatedAsyncioTestCase):
    @patch("daemon.logger.get_logger")
    async def test__logger(self, get_logger_patch: MagicMock):
        get_logger_patch.side_effect = {"daemon.main": (logger := MagicMock())}.get

        main_ = import_module("daemon.main")

        get_logger_patch.assert_has_calls([call("daemon.main"), call("uvicorn")], any_order=True)
        self.assertEqual(logger, main_.logger)

    @patch("sys.exit")
    @patch("daemon.main.logger")
    @patch("daemon.main.API_TOKEN", "token")
    async def test__check_api_token__token_set(self, logger_patch: MagicMock, exit_patch: MagicMock):
        main.check_api_token()

        logger_patch.warning.assert_not_called()
        logger_patch.error.assert_not_called()
        exit_patch.assert_not_called()

    @patch("sys.exit")
    @patch("daemon.main.logger")
    @patch("daemon.main.DEBUG", True)
    @patch("daemon.main.API_TOKEN", "")
    async def test__check_api_token__no_token_debug(self, logger_patch: MagicMock, exit_patch: MagicMock):
        main.check_api_token()

        logger_patch.warning.assert_called_once()
        logger_patch.error.assert_not_called()
        exit_patch.assert_not_called()

    @patch("sys.exit")
    @patch("daemon.main.logger")
    @patch("daemon.main.DEBUG", False)
    @patch("daemon.main.API_TOKEN", "")
    async def test__check_api_token__no_token_prod(self, logger_patch: MagicMock, exit_patch: MagicMock):
        exit_patch.side_effect = lambda *_: logger_patch.error.assert_called_once()

        main.check_api_token()

        logger_patch.warning.assert_not_called()
        exit_patch.assert_called_once_with(1)

    @patch("daemon.main.RELOAD")
    @patch("daemon.main.PORT")
    @patch("daemon.main.HOST")
    @patch("daemon.main.uvicorn.run")
    async def test__run_daemon(
        self,
        uvicorn_run_patch: MagicMock,
        host_patch: MagicMock,
        port_patch: MagicMock,
        reload_patch: MagicMock,
    ):
        main.run_daemon()

        uvicorn_run_patch.assert_called_once_with(
            "daemon.daemon:app",
            host=host_patch,
            port=port_patch,
            reload=reload_patch,
            log_config=None,
        )

    @patch("daemon.main.run_daemon")
    @patch("daemon.main.check_api_token")
    @patch("daemon.main.app")
    @patch("daemon.main.setup_sentry")
    @patch("daemon.main.SENTRY_DSN")
    async def test__main__sentry(
        self,
        sentry_dsn_patch: MagicMock,
        setup_sentry_patch: MagicMock,
        app_patch: MagicMock,
        check_api_token_patch: MagicMock,
        run_daemon_patch: MagicMock,
    ):
        check_api_token_patch.side_effect = lambda: setup_sentry_patch.assert_called_once_with(
            app_patch,
            sentry_dsn_patch,
            "python-daemon",
            "0.1.0",
        )
        run_daemon_patch.side_effect = lambda: check_api_token_patch.assert_called_once_with()

        main.main()

        run_daemon_patch.assert_called_once_with()

    @patch("daemon.main.run_daemon")
    @patch("daemon.main.check_api_token")
    @patch("daemon.main.setup_sentry")
    @patch("daemon.main.SENTRY_DSN", "")
    async def test__main__no_sentry(
        self,
        setup_sentry_patch: MagicMock,
        check_api_token_patch: MagicMock,
        run_daemon_patch: MagicMock,
    ):
        run_daemon_patch.side_effect = lambda: check_api_token_patch.assert_called_once_with()

        main.main()

        run_daemon_patch.assert_called_once_with()
        setup_sentry_patch.assert_not_called()

    @patch("daemon.main.main")
    async def test__main(self, main_patch: MagicMock):
        run_module("daemon")

        main_patch.assert_called_once_with()
