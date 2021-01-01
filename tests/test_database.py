from unittest import TestCase
from unittest.mock import patch, Mock

from database.database import DB, get_database
from utils import import_module


class TestDatabase(TestCase):
    @patch("database.database.declarative_base")
    @patch("database.database.scoped_session")
    @patch("database.database.sessionmaker")
    @patch("database.database.create_engine")
    def test__init(self, create_engine_patch, sessionmaker_patch, scoped_session_patch, declarative_base_patch):
        echo = Mock()

        db = DB("postgresql://testhost:1337", "testdb", "foo", "bar", echo)

        create_engine_patch.assert_called_with(
            "postgresql://foo:bar@testhost:1337/testdb",
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=echo,
        )
        self.assertEqual(create_engine_patch(), db.engine)

        sessionmaker_patch.assert_called_with(bind=db.engine)
        self.assertEqual(sessionmaker_patch(), db._SessionFactory)

        scoped_session_patch.assert_called_with(db._SessionFactory)
        self.assertEqual(scoped_session_patch(), db._Session)

        declarative_base_patch.assert_called_with()
        self.assertEqual(declarative_base_patch(), db.Base)

    def test__add(self):
        db = Mock()
        obj = Mock()

        result = DB.add(db, obj)

        db.session.add.assert_called_with(obj)
        self.assertEqual(obj, result)

    def test__delete(self):
        db = Mock()
        obj = Mock()

        result = DB.delete(db, obj)

        db.session.delete.assert_called_with(obj)
        self.assertEqual(obj, result)

    def test__query(self):
        db = Mock()
        entities = [1, 2, 3, 4]
        kwargs = {"foo": "bar", "xy": "z"}

        result = DB.query(db, *entities, **kwargs)

        db.session.query.assert_called_with(*entities, **kwargs)
        self.assertEqual(db.session.query(), result)

    def test__commit(self):
        db = Mock()

        DB.commit(db)

        db.session.commit.assert_called_with()

    def test__close(self):
        db = Mock()

        DB.close(db)

        db._Session.remove.assert_called_with()

    def test__session(self):
        db = Mock()

        # noinspection PyArgumentList
        result = DB.session.fget(db)

        db._Session.assert_called_with()
        self.assertEqual(db._Session(), result)

    @patch("database.database.SQL_SHOW_STATEMENTS")
    @patch("database.database.SQL_SERVER_PASSWORD")
    @patch("database.database.SQL_SERVER_USERNAME")
    @patch("database.database.SQL_SERVER_DATABASE")
    @patch("database.database.SQL_SERVER_LOCATION")
    @patch("database.database.DB")
    def test__get_database(self, db_patch, location_patch, database_patch, username_patch, password_patch, echo_patch):
        result = get_database()

        db_patch.assert_called_with(
            location=location_patch,
            database=database_patch,
            username=username_patch,
            password=password_patch,
            echo=echo_patch,
        )
        self.assertEqual(db_patch(), result)

    @patch("database.database.get_database")
    def test__db(self, get_database_patch):
        database = import_module("database")

        get_database_patch.assert_called_with()
        self.assertEqual(get_database_patch(), database.db)
