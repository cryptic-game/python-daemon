import importlib
import inspect
import re
import runpy
import sys
from collections import namedtuple
from typing import Optional
from unittest.mock import MagicMock

from daemon import endpoint_collection


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def mock_list(size) -> list[MagicMock]:
    return [MagicMock() for _ in range(size)]


def mock_dict(size, string_keys: bool = False) -> dict[MagicMock, MagicMock]:
    return {(str(MagicMock()) if string_keys else MagicMock()): MagicMock() for _ in range(size)}


def import_module(name: str):
    if module := sys.modules.get(name):
        return importlib.reload(module)

    return __import__(name)


def run_module(module: str):
    runpy.run_module(module, {}, "__main__")


Endpoint = namedtuple("Endpoint", ["name", "function_name", "kwargs"])


def test_endpoint_collection(
    self,
    collection_name: str,
    expected_endpoints: list[Endpoint],
    description: str,
    **collection_kwargs,
):
    import_module("daemon.endpoints")
    _endpoint_collection = endpoint_collection.EndpointCollection
    endpoint_collection_patch = endpoint_collection.EndpointCollection = MagicMock()
    endpoints = {}

    def side_effect(name: Optional[str] = None, *args, **kwargs):
        def deco(f):
            _name = name or f.__name__
            self.assertNotIn(_name, endpoints)
            endpoints[_name] = f, args, kwargs
            return f

        return deco

    endpoint_collection_patch().endpoint.side_effect = side_effect
    endpoint_collection_patch.reset_mock()

    try:
        module = import_module(f"daemon.endpoints.{collection_name}")

        endpoint_collection_patch.assert_called_once_with(collection_name, description, **collection_kwargs)
        self.assertEqual(endpoint_collection_patch(), getattr(module, f"{collection_name}_collection"))

        for expected_endpoint in expected_endpoints:
            actual_func, actual_args, actual_kwargs = endpoints.pop(expected_endpoint.name)
            self.assertEqual(getattr(module, expected_endpoint.function_name), actual_func)
            self.assertEqual((), actual_args)
            self.assertEqual(expected_endpoint.kwargs, actual_kwargs)

            lines = list(map(str.strip, actual_func.__doc__.strip().splitlines()))
            self.assertRegex(lines.pop(), r"^:return: [^ ].*$")
            arguments = set(inspect.getargs(actual_func.__code__).args)
            while match := re.match(r"^:param ([a-zA-Z\d_]+): [^ ].*$", line := lines.pop()):
                arguments.remove(match.group(1))
            self.assertFalse(line)
            self.assertFalse(arguments)
            self.assertTrue(lines[0])
            self.assertTrue(lines.pop())

        self.assertFalse(endpoints)

    finally:
        endpoint_collection.EndpointCollection = _endpoint_collection
        import_module(f"daemon.endpoints.{collection_name}")
