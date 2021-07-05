from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock

from tests._utils import import_module, AsyncMock


class TestDaemon(IsolatedAsyncioTestCase):
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
        functions = []
        fastapi_patch().middleware().side_effect = functions.append
        fastapi_patch.reset_mock()

        import_module("daemon.daemon")

        fastapi_patch().middleware.assert_called_once_with("http")
        self.assertEqual(1, len(functions))
        (db_session,) = functions

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
