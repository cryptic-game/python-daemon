from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch, AsyncMock

from fastapi import HTTPException
from fastapi.openapi.models import HTTPBearer

from daemon.authorization import HTTPAuthorization


class TestAuthorization(IsolatedAsyncioTestCase):
    @patch("daemon.authorization.API_TOKEN", "TEST_API_TOKEN")
    async def test__init__(self):
        authorization = HTTPAuthorization()

        self.assertEqual(authorization.scheme_name, authorization.__class__.__name__)
        self.assertIsInstance(authorization.model, HTTPBearer)
        self.assertEqual(authorization._token, "TEST_API_TOKEN")

    @patch("daemon.authorization.API_TOKEN", None)
    async def test___check_authorization__without_token(self):
        authorization = HTTPAuthorization()
        request = MagicMock()

        result = await authorization._check_authorization(request)

        self.assertEqual(result, True)

    @patch("daemon.authorization.API_TOKEN", "TEST_API_TOKEN")
    async def test___check_authorization__with_token(self):
        authorization = HTTPAuthorization()
        request = MagicMock()
        request.headers.get.return_value = "Bearer TEST_API_TOKEN"

        result = await authorization._check_authorization(request)

        self.assertEqual(result, True)
        request.headers.get.assert_called_once_with("Authorization")

    @patch("daemon.authorization.API_TOKEN", "TEST_API_TOKEN")
    async def test___check_authorization__with_wrong_token(self):
        authorization = HTTPAuthorization()
        request = MagicMock()
        request.headers.get.return_value = "Bearer TEST_WRONG_API_TOKEN"

        result = await authorization._check_authorization(request)

        self.assertEqual(result, False)
        request.headers.get.assert_called_once_with("Authorization")

    @patch("daemon.authorization.API_TOKEN", "TEST_API_TOKEN")
    @patch("daemon.authorization.HTTPAuthorization._check_authorization")
    async def test__call(self, check_authorization_patch: AsyncMock):
        authorization = HTTPAuthorization()
        request = MagicMock()
        check_authorization_patch.return_value = True

        await authorization.__call__(request)

        check_authorization_patch.assert_called_once_with(request)

    @patch("daemon.authorization.API_TOKEN", "TEST_API_TOKEN")
    @patch("daemon.authorization.HTTPAuthorization._check_authorization")
    async def test__call__with_failed_check(self, check_authorization_patch: AsyncMock):
        authorization = HTTPAuthorization()
        request = MagicMock()
        check_authorization_patch.return_value = False

        with self.assertRaises(HTTPException):
            await authorization.__call__(request)

        check_authorization_patch.assert_called_once_with(request)
