from unittest.mock import MagicMock


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)


def mock_list(size) -> list[MagicMock]:
    return [MagicMock() for _ in range(size)]


def mock_dict(size, string_keys: bool = False) -> dict[MagicMock, MagicMock]:
    return {(str(MagicMock()) if string_keys else MagicMock()): MagicMock() for _ in range(size)}
