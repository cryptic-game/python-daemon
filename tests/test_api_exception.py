from unittest import TestCase
from unittest.mock import MagicMock, patch

from _utils import mock_dict
from daemon.exceptions.api_exception import APIException


class TestApiException(TestCase):
    @patch("daemon.exceptions.api_exception.super")
    def test__constructor(self, super_patch: MagicMock):
        super_patch.return_value = type("", (), {"__init__": MagicMock(return_value=None)})
        kwargs = mock_dict(3)

        exception = APIException(kwargs=kwargs)

        self.assertEqual(kwargs, exception._kwargs["kwargs"])
        super_patch.assert_called_once_with()
        super_patch().__init__.assert_called_once_with()

    def test__make_dict(self):
        exception = MagicMock()
        exception._kwargs = mock_dict(3)

        result = APIException.make_dict(exception)

        self.assertEqual({**exception._kwargs, "error": exception.error}, result)

    @patch("daemon.exceptions.api_exception.JSONResponse")
    def test__make_response(self, json_response_patch: MagicMock):
        exception = MagicMock()
        exception._kwargs = mock_dict(3)

        result = APIException.make_response(exception)

        exception.make_dict.assert_called_once_with()
        json_response_patch.assert_called_once_with(exception.make_dict(), status_code=exception.status_code)
        self.assertEqual(json_response_patch(), result)
