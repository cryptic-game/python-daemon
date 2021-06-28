from contextlib import asynccontextmanager
from contextvars import ContextVar
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, call

from _utils import mock_list, mock_dict
from database import database


class TestDatabase(IsolatedAsyncioTestCase):
    @patch("database.database.sa_select")
    async def test__select__no_args(self, sa_select_patch: MagicMock):
        entity = MagicMock()

        result = database.select(entity)

        sa_select_patch.assert_called_once_with(entity)
        self.assertEqual(sa_select_patch(), result)

    @patch("database.database.selectinload")
    @patch("database.database.sa_select")
    async def test__select__with_args(self, sa_select_patch: MagicMock, selectinload_patch: MagicMock):
        entity = MagicMock()

        result = database.select(
            entity,
            a := MagicMock(),
            b := MagicMock(),
            [c := MagicMock(), d := MagicMock(), e := MagicMock()],
            [f := MagicMock()],
        )

        selectinload_patch.assert_has_calls(
            [
                call(a),
                call(b),
                call(c),
                call().selectinload(d),
                call().selectinload().selectinload(e),
                call(f),
            ],
        )

        sa_select_patch.assert_called_once_with(entity)
        sa_select_patch().options.assert_called_once_with(
            selectinload_patch(),
            selectinload_patch(),
            selectinload_patch().selectinload().selectinload(),
            selectinload_patch(),
        )
        self.assertEqual(sa_select_patch().options(), result)

    @patch("database.database.select")
    async def test__filter_by(self, select_patch: MagicMock):
        cls = MagicMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = database.filter_by(cls, *args, **kwargs)

        select_patch.assert_called_once_with(cls, *args)
        select_patch().filter_by.assert_called_once_with(**kwargs)
        self.assertEqual(select_patch().filter_by(), result)

    @patch("database.database.sa_exists")
    async def test__exists(self, sa_exists_patch: MagicMock):
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = database.exists(*args, **kwargs)

        sa_exists_patch.assert_called_once_with(*args, **kwargs)
        self.assertEqual(sa_exists_patch(), result)

    @patch("database.database.sa_delete")
    async def test__delete(self, sa_delete_patch: MagicMock):
        table = MagicMock()

        result = database.delete(table)

        sa_delete_patch.assert_called_once_with(table)
        self.assertEqual(sa_delete_patch(), result)

    @patch("database.database.declarative_base")
    @patch("database.database.URL.create")
    @patch("database.database.create_async_engine")
    async def test__constructor(
        self,
        create_async_engine_patch: MagicMock,
        url_create_patch: MagicMock,
        declarative_base_patch: MagicMock,
    ):
        driver = MagicMock()
        host = MagicMock()
        port = MagicMock()
        db = MagicMock()
        username = MagicMock()
        password = MagicMock()
        pool_recycle = MagicMock()
        pool_size = MagicMock()
        max_overflow = MagicMock()
        echo = MagicMock()

        result = database.DB(driver, host, port, db, username, password, pool_recycle, pool_size, max_overflow, echo)

        url_create_patch.assert_called_once_with(
            drivername=driver,
            username=username,
            password=password,
            host=host,
            port=port,
            database=db,
        )
        create_async_engine_patch.assert_called_once_with(
            url_create_patch(),
            pool_pre_ping=True,
            pool_recycle=pool_recycle,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
        )
        self.assertEqual(create_async_engine_patch(), result.engine)

        declarative_base_patch.assert_called_once_with()
        self.assertEqual(declarative_base_patch(), result.Base)

        self.assertIsInstance(result._session, ContextVar)
        self.assertEqual("session", result._session.name)
        self.assertEqual(None, result._session.get())

        self.assertIsInstance(result._close_event, ContextVar)
        self.assertEqual("close_event", result._close_event.name)
        self.assertEqual(None, result._close_event.get())

    @patch("database.database.logger.debug")
    async def test__create_tables(self, logger_debug_patch: MagicMock):
        db = MagicMock()

        events = []

        async def run_sync(coro):
            self.assertEqual(db.Base.metadata.create_all, coro)
            events.append(1)

        @asynccontextmanager
        async def context_manager():
            events.append(0)

            conn = MagicMock()
            conn.run_sync = run_sync
            yield conn

            events.append(2)

        db.engine.begin = context_manager

        await database.DB.create_tables(db)

        logger_debug_patch.assert_called_once_with("creating tables")

        self.assertEqual([0, 1, 2], events)
