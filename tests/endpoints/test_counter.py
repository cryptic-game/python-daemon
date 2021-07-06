from unittest import IsolatedAsyncioTestCase

from daemon.exceptions.counter import CounterNotFoundException, WrongPasswordException
from daemon.schemas.counter import ValueResponse, ValueChangedResponse
from daemon.schemas.ok import OKResponse
from daemon.utils import responses
from tests._utils import Endpoint, test_endpoint_collection

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
