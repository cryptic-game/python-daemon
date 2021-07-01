import runpy
from importlib import machinery, util
from unittest.mock import MagicMock


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def mock_list(size) -> list[MagicMock]:
    return [MagicMock() for _ in range(size)]


def mock_dict(size, string_keys: bool = False) -> dict[MagicMock, MagicMock]:
    return {(str(MagicMock()) if string_keys else MagicMock()): MagicMock() for _ in range(size)}


def import_module(module: str):
    return machinery.SourceFileLoader(module, util.find_spec(module).origin).load_module(module)


def run_module(module: str):
    runpy.run_module(module, {}, "__main__")
