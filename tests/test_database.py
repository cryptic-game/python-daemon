from contextlib import asynccontextmanager
from contextvars import ContextVar
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, call

from daemon import database
from _utils import mock_list, mock_dict, AsyncMock
from tests._utils import import_module


class TestDatabase(IsolatedAsyncioTestCase):
    @patch("daemon.database.database.sa_select")
    async def test__select__no_args(self, sa_select_patch: MagicMock):
        entity = MagicMock()

        result = database.database.select(entity)

        sa_select_patch.assert_called_once_with(entity)
        self.assertEqual(sa_select_patch(), result)

    @patch("daemon.database.database.selectinload")
    @patch("daemon.database.database.sa_select")
    async def test__select__with_args(self, sa_select_patch: MagicMock, selectinload_patch: MagicMock):
        entity = MagicMock()

        result = database.database.select(
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

    @patch("daemon.database.database.select")
    async def test__filter_by(self, select_patch: MagicMock):
        cls = MagicMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = database.database.filter_by(cls, *args, **kwargs)

        select_patch.assert_called_once_with(cls, *args)
        select_patch().filter_by.assert_called_once_with(**kwargs)
        self.assertEqual(select_patch().filter_by(), result)

    @patch("daemon.database.database.sa_exists")
    async def test__exists(self, sa_exists_patch: MagicMock):
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = database.database.exists(*args, **kwargs)

        sa_exists_patch.assert_called_once_with(*args, **kwargs)
        self.assertEqual(sa_exists_patch(), result)

    @patch("daemon.database.database.sa_delete")
    async def test__delete(self, sa_delete_patch: MagicMock):
        table = MagicMock()

        result = database.database.delete(table)

        sa_delete_patch.assert_called_once_with(table)
        self.assertEqual(sa_delete_patch(), result)

    @patch("daemon.database.database.declarative_base")
    @patch("daemon.database.database.URL.create")
    @patch("daemon.database.database.create_async_engine")
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

        result = database.database.DB(
            driver,
            host,
            port,
            db,
            username,
            password,
            pool_recycle,
            pool_size,
            max_overflow,
            echo,
        )

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

    @patch("daemon.database.database.logger.debug")
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

        await database.database.DB.create_tables(db)

        logger_debug_patch.assert_called_once_with("creating tables")

        self.assertEqual([0, 1, 2], events)

    async def test__add(self):
        db = MagicMock()
        obj = MagicMock()

        result = await database.database.DB.add(db, obj)

        db.session.add.assert_called_once_with(obj)
        self.assertEqual(obj, result)

    async def test__db__delete(self):
        db = AsyncMock()
        obj = MagicMock()

        result = await database.database.DB.delete(db, obj)

        db.session.delete.assert_called_once_with(obj)
        self.assertEqual(obj, result)

    async def test__exec(self):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = await database.database.DB.exec(db, *args, **kwargs)

        db.session.execute.assert_called_once_with(*args, **kwargs)
        self.assertEqual(db.session.execute(), result)

    async def test__stream(self):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)
        db.session.stream.return_value = MagicMock()

        result = await database.database.DB.stream(db, *args, **kwargs)

        db.session.stream.assert_called_once_with(*args, **kwargs)
        (await db.session.stream()).scalars.assert_called_once_with()
        self.assertEqual((await db.session.stream()).scalars(), result)

    async def test__all(self):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)
        expected = mock_list(5)

        async def async_iterator():
            for x in expected:
                yield x

        db.stream.return_value = async_iterator()

        result = await database.database.DB.all(db, *args, **kwargs)

        db.stream.assert_called_once_with(*args, **kwargs)
        self.assertEqual(expected, result)

    async def test__first(self):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)
        db.exec.return_value = MagicMock()

        result = await database.database.DB.first(db, *args, **kwargs)

        db.exec.assert_called_once_with(*args, **kwargs)
        (await db.exec()).scalar.assert_called_once_with()
        self.assertEqual((await db.exec()).scalar(), result)

    @patch("daemon.database.database.exists")
    async def test__db__exists(self, exists_patch: MagicMock):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = await database.database.DB.exists(db, *args, **kwargs)

        exists_patch.assert_called_once_with(*args, **kwargs)
        exists_patch().select.assert_called_once_with()
        db.first.assert_called_once_with(exists_patch().select())
        self.assertEqual(db.first(exists_patch().select()), result)

    @patch("daemon.database.database.count")
    @patch("daemon.database.database.select")
    async def test__db__count(self, select_patch: MagicMock, count_patch: MagicMock):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = await database.database.DB.count(db, *args, **kwargs)

        count_patch.assert_called_once_with()
        select_patch.assert_called_once_with(count_patch())
        select_patch().select_from.assert_called_once_with(*args, **kwargs)
        db.first.assert_called_once_with(select_patch().select_from())
        self.assertEqual(db.first(), result)

    @patch("daemon.database.database.filter_by")
    async def test__get(self, filter_by_patch: MagicMock):
        db = AsyncMock()
        args = mock_list(5)
        kwargs = mock_dict(5, True)

        result = await database.database.DB.get(db, *args, **kwargs)

        filter_by_patch.assert_called_once_with(*args, **kwargs)
        db.first.assert_called_once_with(filter_by_patch())
        self.assertEqual(db.first(), result)

    async def test__commit__no_session(self):
        db = MagicMock()
        db._session.get.return_value = None
        db.session = AsyncMock()

        await database.database.DB.commit(db)

        db._session.get.assert_called_once_with()
        db.session.commit.assert_not_called()

    async def test__commit__with_session(self):
        db = MagicMock()
        session = db._session.get.return_value = db.session = MagicMock()
        session.commit = AsyncMock()

        await database.database.DB.commit(db)

        db._session.get.assert_called_once_with()
        session.commit.assert_called_once_with()

    async def test__close__no_session(self):
        db = MagicMock()
        db._session.get.return_value = None
        db.session = AsyncMock()

        await database.database.DB.close(db)

        db._session.get.assert_called_once_with()
        db.session.close.assert_not_called()
        db._close_event.get().set.assert_not_called()

    async def test__close__with_session(self):
        db = MagicMock()
        session = db._session.get.return_value = db.session = MagicMock()
        session.close = AsyncMock()

        await database.database.DB.close(db)

        db._session.get.assert_called_once_with()
        session.close.assert_called_once_with()
        db._close_event.get.assert_called_once_with()
        db._close_event.get().set.assert_called_once_with()

    @patch("daemon.database.database.Event")
    @patch("daemon.database.database.AsyncSession")
    async def test__create_session(self, asyncsession_patch: MagicMock, event_patch: MagicMock):
        db = MagicMock()

        result = database.database.DB.create_session(db)

        asyncsession_patch.assert_called_once_with(db.engine)
        db._session.set.assert_called_with(asyncsession_patch())
        event_patch.assert_called_once_with()
        db._close_event.set.assert_called_with(event_patch())
        self.assertEqual(asyncsession_patch(), result)

    async def test__session(self):
        db = MagicMock()

        # noinspection PyArgumentList
        result = database.database.DB.session.fget(db)

        db._session.get.assert_called_once_with()
        self.assertEqual(db._session.get(), result)

    async def test__wait_for_close_event(self):
        db = MagicMock()
        db._close_event.get.return_value = AsyncMock()

        await database.database.DB.wait_for_close_event(db)

        db._close_event.get.assert_called_once_with()
        db._close_event.get().wait.assert_called_once_with()

    @patch("daemon.database.database.SQL_SHOW_STATEMENTS")
    @patch("daemon.database.database.MAX_OVERFLOW")
    @patch("daemon.database.database.POOL_SIZE")
    @patch("daemon.database.database.POOL_RECYCLE")
    @patch("daemon.database.database.DB_PASSWORD")
    @patch("daemon.database.database.DB_USERNAME")
    @patch("daemon.database.database.DB_DATABASE")
    @patch("daemon.database.database.DB_PORT")
    @patch("daemon.database.database.DB_HOST")
    @patch("daemon.database.database.DB_DRIVER")
    @patch("daemon.database.database.DB")
    async def test__get_database(
        self,
        db_patch: MagicMock,
        db_driver_patch: MagicMock,
        db_host_patch: MagicMock(),
        db_port_patch: MagicMock,
        db_database_patch: MagicMock,
        db_username_patch: MagicMock,
        db_password_patch: MagicMock,
        pool_recycle_patch: MagicMock,
        pool_size_patch: MagicMock,
        max_overflow_patch: MagicMock,
        sql_show_statements_patch: MagicMock,
    ):
        result = database.get_database()

        db_patch.assert_called_once_with(
            driver=db_driver_patch,
            host=db_host_patch,
            port=db_port_patch,
            database=db_database_patch,
            username=db_username_patch,
            password=db_password_patch,
            pool_recycle=pool_recycle_patch,
            pool_size=pool_size_patch,
            max_overflow=max_overflow_patch,
            echo=sql_show_statements_patch,
        )
        self.assertEqual(result, db_patch())

    @patch("daemon.database.db")
    async def test__db_context(self, db_patch: MagicMock):
        db_patch.commit = AsyncMock()
        db_patch.close = AsyncMock()
        db_patch.close.side_effect = lambda: db_patch.commit.assert_called_once_with()

        async with database.db_context():
            db_patch.create_session.assert_called_once_with()

        db_patch.close.assert_called_once_with()

    @patch("daemon.database.db_context")
    async def test__db_wrapper(self, db_context_patch: MagicMock):
        events = []
        args = mock_list(5)
        kwargs = mock_dict(5, True)
        expected = MagicMock()

        @database.db_wrapper
        async def test(*_args, **_kwargs):
            self.assertEqual(args, list(_args))
            self.assertEqual(kwargs, _kwargs)
            events.append(1)
            return expected

        @asynccontextmanager
        async def context_manager():
            events.append(0)
            yield
            events.append(2)

        db_context_patch.side_effect = context_manager

        result = await test(*args, **kwargs)

        self.assertEqual(expected, result)
        db_context_patch.assert_called_once_with()
        self.assertEqual([0, 1, 2], events)
        self.assertEqual("test", test.__name__)

    async def test__db(self):
        old_get_database = database.database.get_database
        get_database_mock = database.database.get_database = MagicMock()

        db = import_module("daemon.database")

        get_database_mock.assert_called_once_with()
        database.get_database = old_get_database
        # noinspection PyUnresolvedReferences
        self.assertEqual(get_database_mock(), db.db)
