from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch, AsyncMock

from fastapi import HTTPException

from daemon.authorization import HTTPAuthorization


class TestAuthorization(IsolatedAsyncioTestCase):
    @patch("daemon.authorization.API_TOKEN")
    @patch("daemon.authorization.HTTPBearer")
    async def test__constructor(self, httpbearer_patch: MagicMock, api_token_patch: MagicMock):
        authorization = HTTPAuthorization()

        httpbearer_patch.assert_called_once_with()
        self.assertEqual(httpbearer_patch(), authorization.model)
        self.assertEqual(authorization.__class__.__name__, authorization.scheme_name)
        self.assertEqual(api_token_patch, authorization._token)

    async def test__check_authorization__no_token(self):
        authorization = MagicMock(_token=None)

        result = await HTTPAuthorization._check_authorization(authorization, ...)

        self.assertTrue(result)

    async def test__check_authorization__no_authorization_header(self):
        authorization = MagicMock()
        request = MagicMock()
        request.headers.get.return_value = None

        result = await HTTPAuthorization._check_authorization(authorization, request)

        self.assertFalse(result)
        request.headers.get.assert_called_once_with("Authorization")

    async def test__check_authorization__wrong_token(self):
        authorization = MagicMock()
        request = MagicMock()
        request.headers.get().removeprefix.return_value = MagicMock()
        request.reset_mock()

        result = await HTTPAuthorization._check_authorization(authorization, request)

        self.assertFalse(result)
        request.headers.get.assert_called_once_with("Authorization")
        request.headers.get().removeprefix.assert_called_once_with("Bearer ")

    async def test__check_authorization__correct_token(self):
        authorization = MagicMock()
        request = MagicMock()
        request.headers.get().removeprefix.return_value = authorization._token
        request.reset_mock()

        result = await HTTPAuthorization._check_authorization(authorization, request)

        self.assertTrue(result)
        request.headers.get.assert_called_once_with("Authorization")
        request.headers.get().removeprefix.assert_called_once_with("Bearer ")

    async def test__call__successful(self):
        authorization = MagicMock(_check_authorization=AsyncMock())
        request = MagicMock()
        authorization._check_authorization.return_value = True

        await HTTPAuthorization.__call__(authorization, request)

        authorization._check_authorization.assert_called_once_with(request)

    async def test__call__with_failed_check(self):
        authorization = MagicMock(_check_authorization=AsyncMock())
        request = MagicMock()
        authorization._check_authorization.return_value = False

        with self.assertRaises(HTTPException) as context:
            await HTTPAuthorization.__call__(authorization, request)

        authorization._check_authorization.assert_called_once_with(request)
        self.assertEqual(401, context.exception.status_code)
