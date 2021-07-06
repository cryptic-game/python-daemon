from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from daemon.endpoints import counter
from daemon.exceptions.counter import CounterNotFoundException, WrongPasswordException
from daemon.models.counter import Counter
from daemon.schemas.counter import ValueResponse, ValueChangedResponse
from daemon.schemas.ok import OKResponse
from daemon.utils import responses
from tests._utils import Endpoint, test_endpoint_collection, AsyncMock

ENDPOINTS: list[Endpoint] = [
    Endpoint("exception", "exception", {}),
    Endpoint("get", "get", {"responses": responses(ValueResponse, CounterNotFoundException)}),
    Endpoint("increment", "increment", {"responses": responses(ValueChangedResponse)}),
    Endpoint("reset", "magic", {"responses": responses(OKResponse, CounterNotFoundException)}),
    Endpoint("set", "set_value", {"responses": responses(ValueChangedResponse, WrongPasswordException)}),
]


class TestCounterEndpoints(IsolatedAsyncioTestCase):
    async def test__collection(self):
        test_endpoint_collection(self, "counter", ENDPOINTS, "test endpoints", test=True)

    async def test__exception(self):
        with self.assertRaises(ZeroDivisionError):
            await counter.exception()

    @patch("daemon.endpoints.counter.db")
    async def test__get__not_found(self, db_patch: MagicMock):
        user_id = MagicMock()
        db_patch.get = AsyncMock(return_value=None)

        with self.assertRaises(CounterNotFoundException):
            await counter.get(user_id)

        db_patch.get.assert_called_once_with(Counter, user_id=user_id)

    @patch("daemon.endpoints.counter.db")
    async def test__get__successful(self, db_patch: MagicMock):
        user_id = MagicMock()
        mock = MagicMock()
        db_patch.get = AsyncMock(return_value=mock)

        result = await counter.get(user_id)

        db_patch.get.assert_called_once_with(Counter, user_id=user_id)
        self.assertEqual({"value": mock.value}, result)
