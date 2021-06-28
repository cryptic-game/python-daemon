from unittest.mock import MagicMock


def mock_list(size) -> list[MagicMock]:
    return [MagicMock() for _ in range(size)]


def mock_dict(size, string_keys: bool = False) -> dict[MagicMock, MagicMock]:
    return {(str(MagicMock()) if string_keys else MagicMock()): MagicMock() for _ in range(size)}
