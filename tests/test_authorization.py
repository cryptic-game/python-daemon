from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, Mock

from fastapi import HTTPException

from authorization import HTTPAuthorization


class TestAuthorization(IsolatedAsyncioTestCase):
    @patch("authorization.HTTPAuthorization._check_authorization")
    async def test__call(self, check_authorization_patch):
        check_authorization_patch.side_effect = lambda a: a.ok
        authorization = HTTPAuthorization()

        await authorization(Mock(ok=True))

        with self.assertRaises(HTTPException):
            await authorization(Mock(ok=False))

    @patch("authorization.API_TOKEN")
    async def test__init(self, token_patch):
        authorization = HTTPAuthorization()
        self.assertEqual(token_patch, authorization._token)

    async def test__check_authorization__no_token(self):
        authorization = HTTPAuthorization()
        authorization._token = None

        self.assertEqual(True, await authorization._check_authorization(Mock()))

    async def test__check_authorization__no_auth_header(self):
        authorization = HTTPAuthorization()
        authorization._token = Mock()

        request = Mock()
        request.headers.get.return_value = False

        self.assertEqual(False, await authorization._check_authorization(request))

    async def test__check_authorization__check_token(self):
        authorization = HTTPAuthorization()
        authorization._token = Mock()

        mock = Mock()
        mock.headers.get().removeprefix.return_value = authorization._token
        self.assertEqual(True, await authorization._check_authorization(mock))

        mock.headers.get().removeprefix.return_value = Mock()
        self.assertEqual(False, await authorization._check_authorization(mock))

        mock.headers.get().removeprefix.assert_called_with("Bearer ")
