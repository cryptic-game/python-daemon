from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from tests._utils import import_module, AsyncMock


class TestDaemon(IsolatedAsyncioTestCase):
    def get_decorated_function(self, fastapi_patch: MagicMock, decorator_name, *decorator_args, **decorator_kwargs):
        functions = []
        decorator = MagicMock(side_effect=functions.append)
        getattr(fastapi_patch(), decorator_name).side_effect = (
            lambda *args, **kwargs: decorator if (args, kwargs) == (decorator_args, decorator_kwargs) else MagicMock()
        )
        fastapi_patch.reset_mock()

        module = import_module("daemon.daemon")

        decorator.assert_called_once()
        self.assertEqual(1, len(functions))
        return module, functions[0]

    @patch("daemon.endpoints.register_collections")
    @patch("fastapi.FastAPI")
    async def test__global_vars(self, fastapi_patch: MagicMock, register_collections_patch: MagicMock):
        module = import_module("daemon.daemon")

        fastapi_patch.assert_called_once_with(title="Python Daemon")
        self.assertEqual(fastapi_patch(), module.app)
        register_collections_patch.assert_called_once_with(fastapi_patch())
        self.assertEqual(register_collections_patch(), module.endpoints)

    @patch("daemon.database.db")
    @patch("fastapi.FastAPI")
    async def test__db_session(self, fastapi_patch: MagicMock, db_patch: MagicMock):
        _, db_session = self.get_decorated_function(fastapi_patch, "middleware", "http")

        events = []
        db_patch.create_session.side_effect = lambda: events.append(0)
        expected = MagicMock()
        call_next = AsyncMock(side_effect=lambda _: events.append(1) or expected)
        request = MagicMock()
        db_patch.commit = AsyncMock(side_effect=lambda: events.append(2))
        db_patch.close = AsyncMock(side_effect=lambda: events.append(3))

        result = await db_session(request, call_next)

        self.assertEqual([0, 1, 2, 3], events)
        call_next.assert_called_once_with(request)
        self.assertEqual(expected, result)

    @patch("fastapi.FastAPI")
    async def test__on_startup__no_tables(self, fastapi_patch: MagicMock):
        module, on_startup = self.get_decorated_function(fastapi_patch, "on_event", "startup")

        module.SQL_CREATE_TABLES = False
        db = module.db = AsyncMock()

        await on_startup()

        db.create_tables.assert_not_called()

    @patch("fastapi.FastAPI")
    async def test__on_startup__create_tables(self, fastapi_patch: MagicMock):
        module, on_startup = self.get_decorated_function(fastapi_patch, "on_event", "startup")

        module.SQL_CREATE_TABLES = True
        db = module.db = AsyncMock()

        await on_startup()

        db.create_tables.assert_called_once_with()
