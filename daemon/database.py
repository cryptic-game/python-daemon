from typing import TypeVar

from sqlalchemy import create_engine

# noinspection PyProtectedMember
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session, Query

from config import (
    SQL_SERVER_LOCATION,
    SQL_SERVER_DATABASE,
    SQL_SERVER_USERNAME,
    SQL_SERVER_PASSWORD,
    SQL_SHOW_STATEMENTS,
)

T = TypeVar("T")


class DB:
    """Database connection"""

    def __init__(self, location: str, database: str, username: str, password: str, echo: bool):
        protocol, location = location.split("://")
        self.engine: Engine = create_engine(
            f"{protocol}://{username}:{password}@{location}/{database}",
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20,
            echo=echo,
        )

        self._SessionFactory: sessionmaker = sessionmaker(bind=self.engine)
        self._Session = scoped_session(self._SessionFactory)
        self.Base: DeclarativeMeta = declarative_base()

    def add(self, obj: T) -> T:
        """
        Add a new row to the database

        :param obj: the row to insert
        :return: the same row
        """

        self.session.add(obj)
        return obj

    def delete(self, obj: T) -> T:
        """
        Remove a row from the database

        :param obj: the row to remove
        :return: the same row
        """

        self.session.delete(obj)
        return obj

    def query(self, *entities, **kwargs) -> Query:
        """Shortcut for db.session.query()"""

        return self.session.query(*entities, **kwargs)

    def commit(self):
        """Shortcut for db.session.commit()"""

        self.session.commit()

    def close(self):
        """Close the current session"""

        self._Session.remove()

    @property
    def session(self) -> Session:
        """Get the session object for the current thread"""

        return self._Session()


db = DB(
    location=SQL_SERVER_LOCATION,
    database=SQL_SERVER_DATABASE,
    username=SQL_SERVER_USERNAME,
    password=SQL_SERVER_PASSWORD,
    echo=SQL_SHOW_STATEMENTS,
)
