from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, call

import main
from tests._utils import import_module


class TestMain(IsolatedAsyncioTestCase):
    @patch("logger.get_logger")
    async def test__logger(self, get_logger_patch: MagicMock):
        get_logger_patch.side_effect = {"main": (logger := MagicMock())}.get

        main_ = import_module("main")

        get_logger_patch.assert_has_calls([call("main"), call("uvicorn")], any_order=True)
        self.assertEqual(logger, main_.logger)

    @patch("sys.exit")
    @patch("main.logger")
    @patch("main.API_TOKEN", "token")
    async def test__check_api_token__token_set(self, logger_patch: MagicMock, exit_patch: MagicMock):
        main.check_api_token()

        logger_patch.warning.assert_not_called()
        logger_patch.error.assert_not_called()
        exit_patch.assert_not_called()

    @patch("sys.exit")
    @patch("main.logger")
    @patch("main.DEBUG", True)
    @patch("main.API_TOKEN", "")
    async def test__check_api_token__no_token_debug(self, logger_patch: MagicMock, exit_patch: MagicMock):
        main.check_api_token()

        logger_patch.warning.assert_called_once()
        logger_patch.error.assert_not_called()
        exit_patch.assert_not_called()

    @patch("sys.exit")
    @patch("main.logger")
    @patch("main.DEBUG", False)
    @patch("main.API_TOKEN", "")
    async def test__check_api_token__no_token_prod(self, logger_patch: MagicMock, exit_patch: MagicMock):
        exit_patch.side_effect = lambda *_: logger_patch.error.assert_called_once()

        main.check_api_token()

        logger_patch.warning.assert_not_called()
        exit_patch.assert_called_once_with(1)
