from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from fastapi import HTTPException

from daemon.authorization import HTTPAuthorization


class TestAuthorization(IsolatedAsyncioTestCase):
    async def test__call(self):
        request = MagicMock()
        request.headers.get.return_value = "Bearer TEST_API_TOKEN"
        authorization = HTTPAuthorization()
        authorization._token = "TEST_API_TOKEN"
        await authorization.__call__(request)
        request.headers.get.assert_called_with("Authorization")

    async def test__call__without_token(self):
        request = MagicMock()
        authorization = HTTPAuthorization()
        await authorization.__call__(request)

    async def test__call__with_wrong_token(self):
        request = MagicMock()
        request.headers.get.return_value = "Bearer TEST_API_WRONG_TOKEN"
        authorization = HTTPAuthorization()
        authorization._token = "TEST_API_TOKEN"
        with self.assertRaises(HTTPException):
            await authorization.__call__(request)
        request.headers.get.assert_called_with("Authorization")
